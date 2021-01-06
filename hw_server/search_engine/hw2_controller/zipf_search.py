from django.shortcuts import render
from ..models import Article, Word, StemFreq, OriginFreq
from ..forms import WordForm
from search_engine.parsing_utils import string_to_tokens

def zipf_search(request, subset = 0):
    # for spelling correction
    from spellchecker import SpellChecker

    spell = SpellChecker()

    form = WordForm()
    corrected_keyword = ''
    search_title = ''

    # user search
    if request.method == 'POST':
        form = WordForm(request.POST)
        # get search word
        if form.is_valid():
            # parse and clean (stemming..etc) the keywords
            origin_keyword = form.cleaned_data['keywords']
            misspelled = spell.unknown([origin_keyword])
            corrected_keyword = ''
            search_title = ''
            
            if len(misspelled)!= 0:
                for w in misspelled:
                    corrected_keyword = spell.correction(w)
                search_title = 'Do you mean \"{}\". Showing search results for {}'.format(corrected_keyword,corrected_keyword)
            else:
                corrected_keyword = origin_keyword
                search_title = 'search results for {}'.format(origin_keyword)

    # predefine subset
    elif subset == 0:
        corrected_keyword = 'mask'
        search_title = 'search results for mask'

    elif subset == 1:
        corrected_keyword = '2005'
        search_title = 'search results for 2005'

    elif subset == 2:
        corrected_keyword = 'children'
        search_title = 'search results for children'


    # query for the data subset
    keywords_cleaned = string_to_tokens(corrected_keyword)
    titles = {} # get the target articles names
    articles_pk = [] # get the target articles' pk
    articles_raw_words = {} # get the target articles' abstract raw words

    for i in keywords_cleaned:
        w = Word.objects.filter(context = i[0])

        for j in w:
            mode = j.position.get()
            title = mode.title
            # append article pk
            if mode.pk not in articles_pk:
                articles_pk.append(mode.pk)
                # append raw abstract words
                for k in mode.abstract.split(' '):
                    if k not in articles_raw_words.keys():
                        articles_raw_words[k] = 1
                    else:
                        articles_raw_words[k] += 1
            # append article title
            if title not in titles.keys():
                titles[title] = 1
            else:
                titles[title] += 1

    # sort the dict by value
    titles = {k : v for k, v in sorted(titles.items(), key=lambda  item: item[1], reverse=True)}

    articles_raw_words = {k : v for k, v in sorted(articles_raw_words.items(), key=lambda  item: item[1], reverse=True)}
    
    titles_name = list(titles.keys())
    titles_freq = list(titles.values())

    # get sort article pk
    articles_pk = []
    for i in titles_name:
        a = Article.objects.filter(title=i)[0]
        articles_pk.append(a.pk)


    words = {}
    # get the target articles' words
    for i in articles_pk:
        w = Word.objects.filter(position__id=i)
        for j in w:
            if j.context not in words.keys():
                words[j.context] = 1
            else:
                words[j.context] += 1
    
    # sort the dict by value
    words = {k : v for k, v in sorted(words.items(), key=lambda  item: item[1], reverse=True)}

    # calculate zipf
    # of = OriginFreq.objects.filter(word == )
    # sf = StemFreq.objects.all()
    title = str(corrected_keyword)

    # stemming words
    top100_words = list(words.keys())[:100]
    freq = list(words.values())

    # calculate stemmed covid19 set word rank
    stem_covid_set_freq = []
    stem_covid_set_rank = []
    stem_covid_set_first_pk = StemFreq.objects.filter()[0].pk
    for i in top100_words:
        a = StemFreq.objects.get(word=i)
        stem_covid_set_freq.append(a.frequency)
        stem_covid_set_rank.append(a.pk - stem_covid_set_first_pk)

    # origin words
    top100_words_raw = list(articles_raw_words.keys())[:100]
    freq_raw = list(articles_raw_words.values())

    # calculate original covid19 set word rank
    origin_covid_set_freq = []
    origin_covid_set_rank = []
    origin_covid_set_first_pk = OriginFreq.objects.filter()[0].pk
    for i in top100_words_raw:
        a = OriginFreq.objects.get(word=i)
        origin_covid_set_freq.append(a.frequency)
        origin_covid_set_rank.append(a.pk - origin_covid_set_first_pk)

    return_dict = {'search_title':search_title, 'titles_name' : titles_name,
                'titles_freq': titles_freq, 'chart_title' : title, 'form' : form, 'top_words' : top100_words,
                'freq' : freq, 'top_words_raw' : top100_words_raw, 'freq_raw' : freq_raw,
                'stem_covid_set_freq':stem_covid_set_freq, 'stem_covid_set_rank':stem_covid_set_rank,
                'origin_covid_set_freq':origin_covid_set_freq, 'origin_covid_set_rank':origin_covid_set_rank,
                'article_pk':articles_pk }
    
    return render(request, 'search_engine/chart_search.html', return_dict)
