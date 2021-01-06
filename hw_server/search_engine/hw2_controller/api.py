from ..models import Article, Word, StemFreq, OriginFreq, Bmc
from django.http import HttpResponse, JsonResponse
from search_engine.parsing_utils import string_to_tokens

def search_covid(request):
    w = Word.objects.filter(context = "covid19")

    titles = {}
    for i in w:
        title = i.position.get().title
        if title not in titles.keys():
            titles[title] = 1
        else:
            titles[title] += 1

    # sort the dict by value
    titles = {k : v for k, v in sorted(titles.items(), key=lambda  item: item[1], reverse=True)}

    return JsonResponse(titles)

# an api to import pubmed xml
def import_pubmed(request):
    import pandas as pd
    # read the 10000 files from csv
    num_of_csv = 35
    count = 0
    no10 = []
    for i in range(1,num_of_csv+1):
        dataframe = pd.read_csv('Genetic_disease/{}.csv'.format(i))
        count += dataframe.shape[0]
        if dataframe.shape[0] != 10:
            no10.append(i)
        titles = list(dataframe['title'])
        bg = list(dataframe['Background'])
        method = list(dataframe['Methods'])
        result = list(dataframe['Results'])
        conclusion = list(dataframe['Conclusion'])
        for j in range(len(titles)):
            a = Bmc(title = titles[j], background = bg[j], methods = method[j], results = result[j], conclusion = conclusion[j], subset = "genetic_disease")
            a.save()

    return HttpResponse('import success{}'.format(count))
    # return JsonResponse({'problem csv' : no10})

# an api to create reverse index
def create_revindex(request):
    a = Article.objects.all()
    word_freq = {}
    for i in a:
        for j in string_to_tokens(i.abstract):
            if j[0] != 'nan':
                w = Word(context = j[0], pos_in_a_article = j[1])
                w.save()
                w.position.add(i)

    return HttpResponse('Create Reverse index success')

# create origin word frequency table
def create_origin_freq(request):
    a = Article.objects.all()
    m = {}
    # calculate the freq of each word
    for i in a:
        for j in i.abstract.split(' '):
            if j in m.keys():
                m[j] += 1
            else:
                m[j] = 1

    # sort the dict by value
    m = {k : v for k, v in sorted(m.items(), key=lambda  item: item[1], reverse=True)}

    # save to database
    for j in m.keys():
        of = OriginFreq(word = j, frequency = m[j])
        of.save()

    return HttpResponse('OriginFreq created')

# create stem word frequency table
def create_stem_freq(request):
    a = Article.objects.all()
    word_freq = {}
    for i in a:
        for j in string_to_tokens(i.abstract):
            if j[0] != 'nan':
                if j[0] in word_freq.keys():
                    word_freq[j[0]] += 1
                else:
                    word_freq[j[0]] = 0

    # sort the dict by value
    word_freq = {k : v for k, v in sorted(word_freq.items(), key=lambda  item: item[1], reverse=True)}

    #save to database
    for j in word_freq.keys():
        sf = StemFreq(word = j, frequency = word_freq[j])
        sf.save()

    return HttpResponse('StemFreq created')
