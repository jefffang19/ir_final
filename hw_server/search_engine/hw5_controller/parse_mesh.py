from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from ..forms import WordForm
from ..models import Article, BsbiBlocks, PositionInDoc, Bsbi, Spimi

from .utils import find_all, parse_mesh_func, create_mesh_spell_check_dict, mesh_spell_check

import numpy as np  # array handling

from django.views.decorators.csrf import csrf_exempt

def parse_mesh(request):
    mesh = open('../c2020.bin')

    # read covid-19 related NM
    f = open('../mesh_nm')
    _covid_term = f.readlines()
    # remove newline
    covid_term = []
    for i in range(len(_covid_term)-1):
        covid_term.append(_covid_term[i][:-1])

    covid_term.append(_covid_term[len(_covid_term)-1])

    print(covid_term)

    # deal with the first line
    line = mesh.readline()

    # word : [Synonyms]
    index = {}

    # Synonym : word
    inverted_index = {}

    _index = ''
    while line:
        line = mesh.readline()
        if line == '*NEWRECORD\n':
            _index = ''
        elif line[:2] == 'NM' and line[:5] != 'NM_TH':
            # print(line, end='')
            _index = line[5:-1]
            #         print(_index)

            # create a synonyms index
            index[_index] = [_index]

        elif line[:2] == 'SY':
            # print(line, end='')

            # append to synonyms index
            index[_index].append(line[5:].split('|')[0])
            # create a inverted index
            inverted_index[line[5:].split('|')[0]] = _index

    # filter out words without covid19
    filt_index = {}
    for i in index.keys():
        if i in covid_term:
            filt_index[i] = index[i]


    # return JsonResponse(inverted_index)
    # return HttpResponse(len(inverted_index))
    # return HttpResponse([index.values()])
    return JsonResponse(filt_index)

def bsbi(request):
    articles_set = Article.objects.all()
    # articles = []
    #
    # # get all article
    # for i in articles_set:
    #     articles.append(i.abstract)

    # get mesh dictionary (covid-19 related)
    mesh, mesh_inv = parse_mesh_func()

    bsbi_dict = {}

    # count time
    import time

    start_time = time.time()

    # find mesh term
    for cnt, art in enumerate(articles_set):
        print(cnt)
        for mesh_term in mesh_inv.keys():
            # print(art.pk)
            pos = list(find_all(art.abstract, mesh_term))

            if mesh_inv[mesh_term] not in bsbi_dict:
                bsbi_dict[mesh_inv[mesh_term]] = []

            # mesh term exist
            if len(pos) != 0:
                posins = []
                posins_db = []
                for p in pos:
                    # make dictionary
                    pos_dict = {}
                    pos_dict['article_id'] = art.pk
                    pos_dict['position'] = p
                    pos_dict['origin_term'] = mesh_term
                    posins.append(pos_dict)

                    # write to db
                    posin = PositionInDoc(article_id = art.pk, position = p, origin_term = mesh_term)
                    posin.save()
                    posins_db.append(posin)

                # write to db
                b = BsbiBlocks(term = mesh_inv[mesh_term])
                b.save()
                b.position.add(art)
                for _cnt, j in enumerate(posins):
                    # add to dictionary
                    bsbi_dict[mesh_inv[mesh_term]].append(j)
                    # add to db
                    b.pos_in_a_article.add(posins_db[_cnt])

    # sort the dict by key
    bsbi_dict = {k: v for k, v in sorted(bsbi_dict.items(), key=lambda item: item[0], reverse=True)}
    # sort the value list
    for term in bsbi_dict.keys():
        bsbi_dict[term] = [t for t in sorted(bsbi_dict[term], key=lambda item: item['origin_term'], reverse=True)]

    for term in bsbi_dict.keys():
        print(term)
        _term_list = bsbi_dict[term]
        _posins = []
        for i in _term_list:
            posin = PositionInDoc(article_id=i['article_id'], position=i['position'], origin_term=i['origin_term'])
            posin.save()
            _posins.append(posin)

        # save merge block to db
        b = Bsbi(term=term)
        b.save()
        for i in _posins:
            b.pos_in_a_artcle.add(i)

    end_time = time.time()


    # return JsonResponse(bsbi_dict)
    return JsonResponse({**{'time cost of bsbi(sec):' : end_time - start_time}, **bsbi_dict})

    # return HttpResponse([sorted(list(bsbi_dict.keys()))])
    # return HttpResponse([list(bsbi_dict.keys())])

def bsbi_spimi_time(request):
    return JsonResponse({"time cost of bsbi(sec):": 1307.847761631012,
                         "time cost of spimi(sec):": 560.0186586380005})


def spimi(request):
    articles_set = Article.objects.all()
    # get mesh dictionary (covid-19 related)
    mesh, mesh_inv = parse_mesh_func()

    spimi_dict = {}

    # count time
    import time

    start_time = time.time()

    # find mesh term
    for cnt, art in enumerate(articles_set):
        print(cnt)
        for mesh_term in mesh_inv.keys():
            # print(art.pk)
            pos = list(find_all(art.abstract, mesh_term))

            if mesh_inv[mesh_term] not in spimi_dict:
                spimi_dict[mesh_inv[mesh_term]] = []

            # mesh term exist
            if len(pos) != 0:
                posins = []
                for p in pos:
                    # make dictionary
                    pos_dict = {}
                    pos_dict['article_id'] = art.pk
                    pos_dict['position'] = p
                    pos_dict['origin_term'] = mesh_term
                    posins.append(pos_dict)

                for _cnt, j in enumerate(posins):
                    # add to dictionary
                    spimi_dict[mesh_inv[mesh_term]].append(j)

    # don't sort with spimi

    for term in spimi_dict.keys():
        print(term)
        _term_list = spimi_dict[term]
        _posins = []
        for i in _term_list:
            posin = PositionInDoc(article_id=i['article_id'], position=i['position'], origin_term=i['origin_term'])
            posin.save()
            _posins.append(posin)

        # save merge block to db
        b = Spimi(term=term)
        b.save()
        for i in _posins:
            b.pos_in_a_artcle.add(i)

    end_time = time.time()

    return JsonResponse({**{'time cost of spimi(sec):': end_time - start_time}, **spimi_dict})

def create_spell_check(request):
    # reference
    # https://pyspellchecker.readthedocs.io/en/latest/quickstart.html

    # write to json file to use in spell checker
    import json

    freq_dict = create_mesh_spell_check_dict()

    with open('spellcheck_dict.json', 'w') as f:
        json.dump(freq_dict, f)


    return JsonResponse(freq_dict)

# test spell check
@csrf_exempt
def spell_check(request):
    if request.method == 'GET':
        is_misspell, correct_word = mesh_spell_check('COviD-19')

        return JsonResponse({'is misspelled': is_misspell, 'correct word': correct_word, 'origin word': 'COviD-19'})
    elif request.method == 'POST':
        origin_keyword = request.POST['keyword']

        is_misspell, correct_word = mesh_spell_check(origin_keyword)

        return JsonResponse({'is misspelled': is_misspell, 'correct word': correct_word, 'origin word': origin_keyword})

    else:
        return HttpResponse('wrong method')