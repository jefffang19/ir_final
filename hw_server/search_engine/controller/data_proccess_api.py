from ..models import Article, Mirna, MirnaFamily, Cancer, Sentence
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

def import_csv(request):
    import pandas as pd
    import os

    journal_path = '../data/journal_list.csv'
    pubmed_path = '../data/csv/'
    pubmed_dir = os.listdir(pubmed_path)

    journal_if = {}

    # get journal impact factors
    df = pd.read_csv(journal_path)
    journals = list(df['journal'])
    impact_factors = list(df['impact_factor'])

    for i in range(len(journals)):
        journal_if[journals[i]] = impact_factors[i]

    # save pubmed articles to database
    for _dir in pubmed_dir:
        csvs = os.listdir(pubmed_path + _dir)

        impact_factors = []

        print('cancer: {}'.format(_dir.split('_')[1]), end='\n')
        print('mi-RNA: {}'.format(_dir.split('_')[2]), end='\n')

        for _csv in csvs:
            df = pd.read_csv('{}/{}/{}'.format(pubmed_path, _dir, _csv))
            titles = list(df['title'])
            abstracts = list(df['abstract'])
            journal = list(df['journal'])

            # look up the journal_if dictionary to see impact factors
            for j in journal:
                impact_factors.append(journal_if[j])

            for i in range(len(titles)):
                a = Article(title=titles[i], abstract=abstracts[i], cancer=_dir.split('_')[1], mirna=_dir.split('_')[2], journal=journal[i], impact_factor=impact_factors[i])
                a.save()

            impact_factors = []


    return JsonResponse(journal_if)

def journal_list(request):
    import pandas as pd

    journal_path = '../data/journal_list.csv'

    journal_if = {}

    df = pd.read_csv(journal_path)
    journals = list(df['journal'])
    impact_factors = list(df['impact_factor'])

    for i in range(len(journals)):
        journal_if[journals[i]] = impact_factors[i]

    return JsonResponse(journal_if)

def insert_mirna(request):
    mirnas_with_family = [
        "miR-34a",
        "miR-143",
        "miR-22",
        "miR-106a",
        "miR-181a",
        "miR-141",
        "miR-15a",
        "miR-25",
        "miR-206",
        "miR-1",
        "miR-183",
        "miR-17",
        "miR-124",
        "miR-26a",
        "miR-21",
        "miR-17-92",
        "miR-184",
        "miR-31"
    ]

    family = [
        'miR-',
        'microRNA-',
    ]

    for i in mirnas_with_family:
        m = Mirna(name=i)
        m.save()

        for j in family:
            m_w_f = MirnaFamily(name='{}{}'.format(j, i.split('miR-')[1]), root=m)
            m_w_f.save()

    other_mirnas = [
        "let-17",
        "LIN28b",
    ]

    for i in other_mirnas:
        m = Mirna(name=i)
        m.save()

        m_w_f = MirnaFamily(name=i, root=m)
        m_w_f.save()

    return HttpResponse()


def insert_cancer(request):
    cancers = [
        "Osteosarcoma",
        "Ewing sarcoma",
        "Chondrosarcoma",
        "Multiple myeloma",
        "Rhabdomyosarcom",
        "Synovial sarcoma",
        "Neuroblastoma",
        "Cholangiocarcinoma",
        "Retinoblastoma",
        "Squamous cell carcinoma",
    ]

    for i in cancers:
        c = Cancer(name=i)
        c.save()

    return HttpResponse()

def expressions():
    expression_keyword = [
        ["promoted", "promotion", "promoter"],
        ["higher expression", "expressing", "overexpression", "overexpressed"],
        ["lower", "poor expression"],
        ["regulates", "regulation", "up-regulated", "upregulated", "upregulation", "up-regulation"],
        ["enhances", "enhancing"],
        ["down-regulated", "downregulation", "down-regulation", " underexpression"],
        ["suppresses", "suppression", "suppressed", "suppressor"],
        ["repression", " repressing"],
        ["increased"],
        ["decreased"],
        ["carcinogenesis"],
        ["inhibited", "inhibition", "inhibitory"],
        ["interacted", "interaction"],
        ["axis"],
        ["mediator", "mediated"],
        ["metastasis"],
        ["target", "target gene"],
        ["oncomir"],
        ["oncogenes"],
        ["markers", "biomarkers"],
        ["p53", "tumor suppressor"]
    ]
    return expression_keyword

def sorted_expression():
    sorted_expression_keyword = []

    for exp in expressions():
        expression_keyword_subgroup = []
        for kywd in exp:
            if kywd not in expression_keyword_subgroup:
                expression_keyword_subgroup.append(kywd)

            # sort by length
            expression_keyword_subgroup = sorted(expression_keyword_subgroup, key=len, reverse=True)

        sorted_expression_keyword.append(expression_keyword_subgroup)

    return sorted_expression_keyword

def process_sentence(request):
    import re
    import nltk

    # get all the article
    a = Article.objects.all()

    all_evidence = []

    # process every abstracts
    for art in a:
        # split sentences
        sent = nltk.sent_tokenize(art.abstract)

        # target
        try:
            miRNAs = [MirnaFamily.objects.filter(root__name=art.mirna)[0], MirnaFamily.objects.filter(root__name=art.mirna)[1]]
        except:
            miRNAs = [MirnaFamily.objects.filter(name=art.mirna)[0]]

        cancer_object = Cancer.objects.filter(name=art.cancer)[0]  # need to convert to lowercase
        cancer = cancer_object.name
        cancer = cancer.lower()

        # search the mirna family
        for miRNA in miRNAs:
            # container for evidence sentences
            evidence = []

            print(miRNA.name)
            print(cancer)

            # find the sentences containing mi-RNA and Cancer
            for s in sent:
                re_result = re.search(miRNA.name, s)  # find mi-RNA
                if re_result != None:
                    re_result = re.search(cancer, s)  # find cancer
                    if re_result != None:
                        evidence.append(s)

            # save the evidence sentences to database
            for s in evidence:
                se = Sentence(sent=s, article=art)
                se.save()
                se.mirna.add(miRNA)
                se.cancer.add(cancer_object)

            all_evidence.append(evidence)


    return HttpResponse([all_evidence])


@csrf_exempt
def get_evidence(request):
    import re

    # user search
    if request.method == 'POST':
        # get search word
        # we do NOT stem in this hw
        search_cancer = request.POST['cancer']
        search_mirna = request.POST['mirna']

        # search for (eg. miR-34 and microRNA-34 )
        mirna_family = []
        for i in MirnaFamily.objects.filter(root__name=search_mirna):
            mirna_family.append(i)

        cancer_object = Cancer.objects.filter(name=search_cancer)[0]

        # get the sentences with evidence expression in it
        evidence_setences = []
        for s in Sentence.objects.filter(mirna = mirna_family[0], cancer = cancer_object):
            evidence_setences.append(s.sent)

        marked_sentences = []

        # now we high light the sentences
        for exp in sorted_expression():
            for kywd in exp:
                marked_sentence = ""

                a = re.search(kywd, evidence_setences[0])
                if a != None:
                    end_mark = False
                    # print sentence with marker
                    for j, w in enumerate(evidence_setences[0]):
                        if (j == a.start() or j == a.end()):
                            if not end_mark:
                                marked_sentence += '<mark>'
                                end_mark = True
                            else:
                                marked_sentence += '</mark>'

                        marked_sentence += str(w)

                    if marked_sentence != "":
                        marked_sentences.append(marked_sentence)
                    break


        return_dict = {
            'mirna': [i.name for i in mirna_family],
            'cancer': cancer_object.name,
            # 'expression': sorted_expression(),
            'evidence_sentences': marked_sentences,
        }

        return JsonResponse(return_dict, safe=False)

    else:
        return HttpResponse('wrong method, use POST')