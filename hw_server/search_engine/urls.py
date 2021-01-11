from django.urls import path

from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('import_csv', views.import_csv, name = 'import_csv'),
    path('journal_list', views.journal_list, name = 'journal_list'),
    path('insert_mirna', views.insert_mirna, name = 'insert_mirna'),
    path('insert_cancer', views.insert_cancer, name = 'insert_cancer'),
    path('process_sentence', views.process_sentence, name = 'process_sentence'),
    path('get_evidence', views.get_evidence, name = 'get_evidence'),
]