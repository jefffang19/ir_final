from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from ..forms import WordForm
from ..models import Article, Bsbi, Spimi, PositionInDoc

from .utils import parse_mesh_func, mesh_spell_check

import numpy as np  # array handling

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def search(request):
    # user search
    if request.method == 'POST':
        # get search word
        # we do NOT stem in this hw
        origin_keyword = request.POST['keyword']

        # do mesh spell check
        _, origin_keyword = mesh_spell_check(origin_keyword)

        # get the bsbi/spimi
        index_method = int(request.POST['bsbi_spimi'])
        sort_by_tf = int(request.POST['tf'])

        # get mesh dictionary
        mesh_dict, inv_mesh_dict = parse_mesh_func()

        # if term not parent mesh term, map to parent
        origin_keyword = inv_mesh_dict[origin_keyword]

        mesh_dict_str = ''
        first = True
        for i in mesh_dict[origin_keyword]:
            if first:
                first = False
            else:
                mesh_dict_str = mesh_dict_str + 'OR '
            mesh_dict_str = mesh_dict_str + '\"' + i + '\"\n'

        docs_set = []
        # bsbi
        if index_method == 0:
            docs_set = PositionInDoc.objects.filter(bsbi__term=origin_keyword)
        # spimi
        elif index_method == 1:
            docs_set = PositionInDoc.objects.filter(spimi__term=origin_keyword)

        # highlight searched word
        search_result = {}
        for i in docs_set:
            appeared_article = Article.objects.get(pk=i.article_id)
            # init a new abstract
            if appeared_article.title not in search_result.keys():
                search_result[appeared_article.title] = {}
                search_result[appeared_article.title]['abstract'] = appeared_article.abstract
                search_result[appeared_article.title]['marker'] = []
                search_result[appeared_article.title]['tf'] = 0

            # check if terms overlap each other
            add_new_marker = True

            for past_marker in search_result[appeared_article.title]['marker']:
                if past_marker[0] == i.position:
                    # print('debug: overlap occurs')
                    # keep the longer term
                    if past_marker[1] < len(i.origin_term):
                        past_marker[1] = len(i.origin_term)

                    add_new_marker = False

            if add_new_marker:
                # save where to draw the marker to abstract
                # [position, <marker> lenght]
                search_result[appeared_article.title]['marker'].append([i.position, len(i.origin_term)])
                search_result[appeared_article.title]['tf'] += 1


        for i in search_result.keys():
            # we draw the marker to abstract in reverse order, so the position won't be screwed up
            search_result[i]['marker'] = sorted(search_result[i]['marker'], key=lambda item: item[0], reverse=True)

            for pos, length in search_result[i]['marker']:
                _abstract = search_result[i]['abstract']
                search_result[i]['abstract'] = _abstract[:pos] + '<mark>' + _abstract[pos:pos + length] + '</mark>' + _abstract[pos + length:]

        # sort by tf
        # sort the dict
        if sort_by_tf == 1:
            _search_result = {k: v for k, v in sorted(search_result.items(), key=lambda item: item[1]['tf'], reverse=True)}
            search_result = _search_result

        # return HttpResponse([search_result])

        weights = [i['tf'] for i in search_result.values()]

        abstracts = [i['abstract'] for i in search_result.values()]

        template_dict = {'weights': weights, 'titles':list(search_result.keys()), 'abstract': abstracts, 'mesh_dict': mesh_dict_str}

        return JsonResponse(template_dict, safe=False)

    elif request.method == 'GET':
        return render(request, "search_engine/hw5.html")

    else:
        return HttpResponse('unsupported method')

def demo_sheet(request):
    return JsonResponse({
        'normal': 'COVID-19',
        'synonym': 'Wuhan coronavirus',
        'misspell': 'COVID-18 vaccine',
    })