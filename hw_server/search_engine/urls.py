from django.urls import path

from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('import_json', views.import_json, name = 'import_json'),
    path('import_xml', views.import_xml, name = 'import_xml'),
    path('show_articles', views.show_articles, name = 'show_articles'),
    # path('search_page', TemplateView.as_view(template_name = 'search_engine/search_page.html') ),
    path('search_page', views.get_keywords, name = 'search_page'),
    path('upload_file', views.upload_file, name = 'upload_file'),
    # hw 2
    path('zipf',views.zipf, name = 'zipf'), # main hw2 url
    path('zipf/<int:opt>',views.zipf, name = 'zipf'),
    path('zipf_search', views.zipf_search, name = 'zipf_search'),
    path('zipf_search/<int:subset>', views.zipf_search, name = 'zipf_search'),
    path('show_pk_article/<int:pk>/<slug:keyword>', views.show_pk_article, name ='show_pk_article'),
    path('zipf_ct', views.zipf_ct, name = 'zipf_ct'),
    # db api urls
    path('import_pubmed', views.import_pubmed, name = 'import_pubmed'),
    path('create_stemfreq', views.create_stem_freq, name = 'create_stem_freq'),
    path('create_originfreq', views.create_origin_freq, name = 'create_origin_freq'),
    path('create_revindex', views.create_revindex, name = 'create_revindex'),
    path('search_covid', views.search_covid, name = 'search_covid'),
    # hw3
    path('create_model', views.create_model, name = 'create_model'),
    path('use_model', views.use_model, name = 'use_model'),
    path('use_model/<int:set>/<int:perplexity>', views.use_model, name = 'use_model'),
    path('tsne', views.tsne, name = 'tsne'),
    path('test_model_similar', views.test_model_similar, name = 'test_model_similar'),
    # hw4
    path('tfidf', views.show_tfidef, name = 'tfidf'),
    path('create_tfidf_vec', views.create_tfidf_vec, name = 'create_tfidf_vec'),
    # hw5
    path('parse_mesh', views.parse_mesh, name = 'parse_mesh'),
    path('bsbi', views.bsbi, name = 'bsbi'),
    path('spimi', views.spimi, name = 'spimi'),
    path('time_cost', views.bsbi_spimi_time, name = 'time_cost'),
    path('hw5_search', views.search, name = 'hw5_search'),
    path('create_spell_check', views.create_spell_check, name = 'create_spell_check'),
    path('spell_check', views.spell_check, name = 'spell_check'),
    path('hw5_sheet', views.demo_sheet, name = 'hw5_sheet'),
]