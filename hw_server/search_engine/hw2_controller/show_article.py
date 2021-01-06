from django.shortcuts import render
from ..models import Article
from search_engine.parsing_utils import string_to_tokens

def show_pk_article(request, pk, keyword):
    a = Article.objects.get(pk = pk)
    tokens = string_to_tokens(a.abstract)
    keyword_stem = string_to_tokens(keyword)

    pos = []
    for w in tokens:
        if keyword_stem[0][0] == w[0]:
            pos.append(w[1])

    _abstract = ""

    # a bug happened because \n
    for j in a.abstract:
        if(j != '\n'):
            _abstract += j
        else:
            _abstract += ' '
            
    render_dict = {'title':a.title, 'abstract' : _abstract.split(' '), 'keyword' : keyword, 'pos':pos}
    
    return render(request, 'search_engine/show_an_article.html', render_dict)
