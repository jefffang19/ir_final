from ..models import Article, Word, StemFreq, OriginFreq, Bmc
from django.http import HttpResponse, JsonResponse

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

            print(len(titles), len(abstracts), len(journal), len(impact_factors))
            impact_factors = []

        print()

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