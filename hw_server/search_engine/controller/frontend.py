from ..models import Article, Mirna, MirnaFamily, Cancer, Sentence
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .data_proccess_api import sorted_expression, expressions

@csrf_exempt
def get_evidence(request):
    import re

    # user search
    if request.method == 'POST':
        # get search word
        # we do NOT stem in this hw
        search_cancer = request.POST['cancer']
        search_mirna = request.POST['mirna']

        print(search_cancer, search_mirna)

        # search for (eg. miR-34 and microRNA-34 )
        mirna_family = []
        for i in MirnaFamily.objects.filter(root__name=search_mirna):
            mirna_family.append(i)

        cancer_object = Cancer.objects.filter(name=search_cancer)[0]

        # get the sentences with evidence expression in it
        evidence_setences = []
        evidence_setences_objects = []
        for s in Sentence.objects.filter(mirna = mirna_family[0], cancer = cancer_object):
            evidence_setences_objects.append(s)
            evidence_setences.append(s.sent)

        # search for all the articles
        all_mark_setences = []
        come_from_journel = []
        come_from_journel_if = []
        for cnt, evid_sent in enumerate(evidence_setences):
            # print(evid_sent)
            # find mirna and cancer location in a sentence
            mirna_loc = []
            cancer_loc = []
            a = re.search(mirna_family[0].name.lower(), evid_sent.lower())  # find mi-RNA
            if a != None:
                mirna_loc = [a.start(), a.end()]
                a = re.search(cancer_object.name.lower(), evid_sent.lower())  # find cancer
                if a != None:
                    cancer_loc = [a.start(), a.end()]

            expressions_loc = []

            # now we high light the sentences
            for exp in sorted_expression():
                for kywd in exp:
                    a = re.search(kywd, evid_sent.lower())
                    if a != None:
                        expressions_loc.append([a.start(), a.end()])

            # if no expressions_loc
            if len(expressions_loc) == 0:
                continue
            # else:
            #     print(expressions_loc)

            # decide when to use <mark> and </mark>
            end_mark_exp = False
            end_mark_can = False
            end_mark_mi = False
            marked_sentence = ''

            # print sentence with marker
            for j, w in enumerate(evid_sent):
                for exp_loc in expressions_loc:
                    if (j == exp_loc[0] or j == exp_loc[1]):
                        if not end_mark_exp:
                            marked_sentence += '<a href="#" class="text-white bg-primary">'
                            end_mark_exp = True
                        else:
                            marked_sentence += '</a>'
                            end_mark_exp = False

                if (j == cancer_loc[0] or j == cancer_loc[1]):
                    if not end_mark_can:
                        marked_sentence += '<a href="#" class="text-white bg-success">'
                        end_mark_can = True
                    else:
                        marked_sentence += '</a>'
                elif (j == mirna_loc[0] or j == mirna_loc[1]):
                    if not end_mark_mi:
                        marked_sentence += '<a href="#" class="text-white bg-danger">'
                        end_mark_mi = True
                    else:
                        marked_sentence += '</a>'

                marked_sentence += str(w)

            if marked_sentence != "" and marked_sentence not in all_mark_setences:
                all_mark_setences.append(marked_sentence)
                come_from_journel.append(evidence_setences_objects[cnt].article.journal)
                come_from_journel_if.append(evidence_setences_objects[cnt].article.impact_factor)


        evid_jour_if_pair = [[all_mark_setences[i], come_from_journel[i], come_from_journel_if[i]] for i in range(len(come_from_journel))]

        # sort by impact factor
        sorted_evid_jour_if_pair = sorted(evid_jour_if_pair, key=lambda s: s[2], reverse=True)

        all_mark_setences = [i[0] for i in sorted_evid_jour_if_pair]
        come_from_journel = [i[1] for i in sorted_evid_jour_if_pair]
        come_from_journel_if = [i[2] for i in sorted_evid_jour_if_pair]

        # calculate score
        # key senteces * num of articles * ( avg impact factor )
        # we +1 for all impact factor because there is some journals whose impact factor is zero
        arts = Article.objects.filter(cancer=search_cancer, mirna=search_mirna)
        impact_factors = [i.impact_factor + 1 for i in arts]

        import numpy as np

        avg_if = 0
        if len(impact_factors) != 0:
            avg_if = np.mean(np.array(impact_factors))

        print(len(arts))
        evidence_score = len(all_mark_setences) * len(arts) * avg_if

        return_dict = {
            'mirna': [i.name for i in mirna_family],
            'cancer': cancer_object.name,
            # 'expression': sorted_expression(),
            'evidence_sentences': all_mark_setences,
            'journals': come_from_journel,
            'impact_factors': come_from_journel_if,
            'evidence_score': evidence_score
            # 'evid_jour_if_pair': sorted_evid_jour_if_pair
        }

        return JsonResponse(return_dict, safe=False)

    else:
        return render(request, "search_engine/final.html")