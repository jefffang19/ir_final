from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from ..forms import WordForm

from .tfidf_algorithm import tfidf, tfidf_vec, cos_sim, cos_sim_para
import numpy as np  # array handling

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def show_tfidef(request):
    # user search
    if request.method == 'POST':
        # get search word
        # we do NOT stem in this hw
        origin_keyword = request.POST['keyword']
        # get the tfidf method user chose
        tfidf_method = [int(request.POST['ltf']), int(request.POST['lidf']), int(request.POST['rtf']), int(request.POST['ridf'])]

        l_tfidf = tfidf(origin_keyword, tfidf_method[0], tfidf_method[1], int(request.POST['ldata']))
        l_tfidf.sort(key=lambda x: x[1], reverse=True)
        r_tfidf = tfidf(origin_keyword, tfidf_method[2], tfidf_method[3], int(request.POST['rdata']))
        r_tfidf.sort(key=lambda x: x[1], reverse=True)

        # prepare data for template
        docs_ranking_l = [i[0] for i in l_tfidf]
        docs_weight_l = [i[1] for i in l_tfidf]
        docs_len_l = [i[2] for i in l_tfidf]
        docs_ranking_r = [i[0] for i in r_tfidf]
        docs_weight_r = [i[1] for i in r_tfidf]
        docs_len_r = [i[2] for i in r_tfidf]

        # display formula images
        available_formula = ['images/tf_raw_count.png', 'images/tf_term_frequency.png',
                             'images/tf_log_normalization.png',
                             'images/idf_inverse_document_frequency.png', 'images/idf_unary.png',
                             'images/idf_inverse_document_frequency_smooth.png']

        template_dict = {'l_titles': docs_ranking_l, 'l_weights': docs_weight_l, 'l_len': docs_len_l,
                         'r_titles': docs_ranking_r, 'r_weights': docs_weight_r, 'r_len': docs_len_r,
                         'formula': available_formula, 'lpara': [' ' for i in range(len(docs_ranking_l))], 'rpara': [' ' for i in range(len(docs_ranking_r))]}
        # return render(request, "search_engine/tfidf.html", template_dict)
        return JsonResponse(template_dict, safe=False)

    elif request.method == 'GET':
        available_formula = ['images/tf_raw_count.png', 'images/tf_term_frequency.png',
                             'images/tf_log_normalization.png',
                             'images/idf_inverse_document_frequency.png', 'images/idf_unary.png',
                             'images/idf_inverse_document_frequency_smooth.png']

        template_dict = {'formula': available_formula}
        return render(request, "search_engine/tfidf.html", template_dict)

    else:
        return HttpResponse('unsupported method')

@csrf_exempt
def create_tfidf_vec(request):
    # user search
    if request.method == 'POST':
        origin_keyword = request.POST['keyword']
        tfidf_method = [int(request.POST['ltf']), int(request.POST['lidf']), int(request.POST['rtf']),
                        int(request.POST['ridf'])]
        l_vec, l_titles, l_len, bg, mt, rt, con = tfidf_vec(origin_keyword, tfidf_method[0], tfidf_method[1], int(request.POST['ldata']))
        l_cos = cos_sim(l_vec)

        paragraph = ['background', 'method', 'result', 'conclusion']

        l_paragraph = cos_sim_para(l_vec[0], bg, mt, rt, con)
        _l_para = [paragraph[i] for i in l_paragraph]
        l_paragraph = _l_para

        print(l_paragraph)
        left = []
        for i in range(len(l_cos)):
            left.append([l_titles[i], l_cos[i], l_len[i], l_paragraph[i]])
        left.sort(key=lambda x: x[1], reverse=True)

        r_vec, r_titles, r_len, bg, mt, rt, con = tfidf_vec(origin_keyword, tfidf_method[2], tfidf_method[3], int(request.POST['rdata']))
        r_cos = cos_sim(r_vec)
        r_paragraph = cos_sim_para(r_vec[0], bg, mt, rt, con)
        _r_para = [paragraph[i] for i in r_paragraph]
        r_paragraph = _r_para

        right = []
        for i in range(len(r_cos)):
            right.append([r_titles[i], r_cos[i], r_len[i], r_paragraph[i]])
        right.sort(key=lambda x: x[1], reverse=True)

        # prepare data for template
        docs_ranking_l = [i[0] for i in left]
        docs_weight_l = [i[1] for i in left]
        docs_len_l = [i[2] for i in left]
        docs_paragraph_l = [i[3] for i in left]
        docs_ranking_r = [i[0] for i in right]
        docs_weight_r = [i[1] for i in right]
        docs_len_r = [i[2] for i in right]
        docs_paragraph_r = [i[3] for i in right]

        # display formula images
        available_formula = ['images/tf_raw_count.png', 'images/tf_term_frequency.png',
                             'images/tf_log_normalization.png',
                             'images/idf_inverse_document_frequency.png', 'images/idf_unary.png',
                             'images/idf_inverse_document_frequency_smooth.png']

        template_dict = {'l_titles': docs_ranking_l, 'l_weights': docs_weight_l, 'l_len': docs_len_l,
                         'r_titles': docs_ranking_r, 'r_weights': docs_weight_r, 'r_len': docs_len_r,
                         'formula': available_formula, 'lpara': docs_paragraph_l, 'rpara': docs_paragraph_r}
        # return render(request, "search_engine/tfidf.html", template_dict)
        return JsonResponse(template_dict, safe=False)