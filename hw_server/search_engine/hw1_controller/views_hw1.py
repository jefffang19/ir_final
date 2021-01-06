from django.shortcuts import render
from ..models import Article, Word
from django.http import HttpResponse
from django.template import loader
from ..forms import WordForm, UploadFileForm


from search_engine.parsing_utils import data_processor, handle_uploaded_file, count_sent
from search_engine.parsing_utils import string_to_tokens

# api function
def import_json(request):
    file_path = 'temp_uploaded'
    article_words = data_processor(file_path, mode = 'json', tag = "tweet_text")
    for i in article_words:
        a = Article(abstract = i['sentence'])
        a.save()
        for j in i['words']:
            w = Word(context = j[0], pos_in_a_article = j[1])
            w.save()
            w.position.add(a)

    # return JsonResponse({"Import file" : "Json", "Status" : "Success"})

    return show_articles(request, True)

# api function
def import_xml(request):
    file_path = 'temp_uploaded'
    many_article = data_processor(file_path, mode = 'xml', tag = 'abstract')

    # debug
    # return HttpResponse(len(many_article))

    for i in many_article:
        a = Article(abstract = i['sentence'])
        a.save()
        for j in i['words']:
            w = Word(context = j[0], pos_in_a_article = j[1])
            w.save()
            w.position.add(a)
        

    # return JsonResponse({"Import file" : "xml", "Status" : "Success"})
    return show_articles(request, True)

# main func
def show_articles(request, first=False):
    # POST => process the form data from user
    # if request.method == 'POST':
    if not first and request.method == 'POST':
        form = WordForm(request.POST)
        if form.is_valid():
            # parse and clean (stemming..etc) the keywords
            keywords_cleaned = string_to_tokens(form.cleaned_data['keywords'])
            # search keywords in db (Model => Word)
            all_words = []
            for i in keywords_cleaned:
                # retrive all word
                q_set = Word.objects.filter(context=i[0])
                for j in q_set:
                    temp = {}
                    temp['word'] = j.context # keyword name
                    temp['pos'] = j.pos_in_a_article # position in the doc
                    # look up in which docs
                    # get many to many table
                    q_art = j.position.get()

                    # when calculating the which doc, we do ( pk - current_firstpk )
                    q3 = Article.objects.filter()[0]
                    article_firstpk = q3.pk

                    temp['docs'] = q_art.pk - article_firstpk

                    all_words.append(temp)


            # now we render the show page
            all_articles = Article.objects.all()

            len_article = len(all_articles) #count the num of articles

            arts = []
            _str = ""

            # a bug happened because \n
            for i in all_articles:
                for j in i.abstract:
                    if(j != '\n'):
                        _str += j
                    else:
                        _str += ' '
                    
                arts.append(_str)
                _str = ""


            arts = [i.split(' ') for i in arts] # articles break into words
            
            # count sentence num
            tot_sc = 0
            sep_sc = []
            for sc in all_articles:
                tot_sc += count_sent(sc.abstract)
                sep_sc.append(count_sent(sc.abstract))

            # count the num of words
            tot_words = 0
            len_sep_words = []
            
            for wo in arts:
                tot_words += len(wo)
                len_sep_words.append(len(wo))

            # make sure which docs has keywords
            # format : [doc1, doc2, doc3] (type int)
            key_docs = []
            for i in all_words:
                if i['docs'] not in key_docs:
                    key_docs.append(i['docs'])

            # make sure where the keywords are in the coresponding doc
            # format : {doc1 : [pos1, pos2], doc2 : [pos3, pos4]}  (type int)
            key_pos = {}
            for i in all_words:
                if i['docs'] not in key_pos.keys():
                    key_pos[i['docs']] = [i['pos'],]
                else:
                    key_pos[i['docs']].append(i['pos'])

            
            form = WordForm()


            #count

            words = {'form' : form, 'len_article': len_article ,'tot_sc' : tot_sc ,'sep_sc':sep_sc , 'len_words' : tot_words, 'sep_words':len_sep_words, 'articles' :  arts, 'num_result' : len(all_words) , 'keylines' : key_docs  , 'keywords' : key_pos }
            # structure of words
            # {
            #   'articles' : a list of articles to show on template,
            #   'keylines' : a list of which line has words to highlight,
            #   'keywords' : a dict of which word to highlight in the corresponding line,
            #                   key is int , value is list 
            # }

            # debug
            # return JsonResponse({'keylines' : key_docs  , 'keywords' : key_pos})

            return render(request, 'search_engine/show_articles.html', words)
    

    else:
        form = WordForm()
        all_articles = Article.objects.all()

        len_article = len(all_articles) #count the num of articles
        arts = [i.abstract.split(' ') for i in all_articles] # articles break into words
        # count the num of words
        tot_words = 0
        len_sep_words = []

        # count sent num
        tot_sc = 0
        sep_sc = []
        for sc in all_articles:
            tot_sc += count_sent(sc.abstract)
            sep_sc.append(count_sent(sc.abstract))
        
        for wo in arts:
            tot_words += len(wo)
            len_sep_words.append(len(wo))
        words = {'form':form, 'articles' : [i.abstract.split(' ') for i in all_articles] ,'tot_sc' : tot_sc ,'sep_sc':sep_sc , 'len_article' : len_article  , 'len_words' : tot_words, 'sep_words':len_sep_words,}
        
        # return HttpResponse(loader.get_template('search_engine/show_articles.html').render(words , request))
        return render(request, 'search_engine/show_articles.html', words)


# deprecated
def get_keywords(request):

    # POST => process the form data from user
    if request.method == 'POST':
        form = WordForm(request.POST)
        if form.is_valid():
            # parse and clean (stemming..etc) the keywords
            keywords_cleaned = string_to_tokens(form.cleaned_data['keywords'])
            # search keywords in db (Model => Word)
            all_words = []
            for i in keywords_cleaned:
                # retrive all word
                q_set = Word.objects.filter(context=i[0])
                for j in q_set:
                    temp = {}
                    temp['word'] = j.context # keyword name
                    temp['pos'] = j.pos_in_a_article # position in the doc
                    # look up in which docs
                    # get many to many table
                    q_art = j.position.get()

                    # when calculating the which doc, we do ( pk - current_firstpk )
                    q3 = Article.objects.filter()[0]
                    article_firstpk = q3.pk

                    temp['docs'] = q_art.pk - article_firstpk


                    all_words.append(temp)
            
            # now we render the show page
            all_articles = Article.objects.all()

            # make sure which docs has keywords
            # format : [doc1, doc2, doc3] (type int)
            key_docs = []
            for i in all_words:
                if i['docs'] not in key_docs:
                    key_docs.append(i['docs'])

            # make sure where the keywords are in the coresponding doc
            # format : {doc1 : [pos1, pos2], doc2 : [pos3, pos4]}  (type int)
            key_pos = {}
            for i in all_words:
                if i['docs'] not in key_pos.keys():
                    key_pos[i['docs']] = [i['pos'],]
                else:
                    key_pos[i['docs']].append(i['pos'])

            

            words = {'articles' : [i.abstract.split(' ') for i in all_articles] , 'num_result' : len(all_words) , 'keylines' : key_docs  , 'keywords' : key_pos }
    
            return HttpResponse(loader.get_template('search_engine/show_articles.html').render(words , request))

            # return HttpResponse(all_words)

    # GET => create blank form
    else:
        form = WordForm()

    return render(request, 'search_engine/search_page.html', {'form' : form})

def upload_file(request):
    if request.method == 'POST':
        del_everything(request)
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # store the uploaded file
            handle_uploaded_file(request.FILES['file'])
            if request.POST['mode'] == 'xml':
               return import_xml(request)
            elif request.POST['mode'] == 'json':
                return import_json(request)
            else:
                return HttpResponse('upload success, but wrong mode')
        else:
            return HttpResponse('upload unsuccessful')

    else:
        form = UploadFileForm()

    return render(request, 'search_engine/upload_file_abstract.html', {'form' : form})

def del_everything(request):
    Article.objects.all().delete()
    Word.objects.all().delete()

    return