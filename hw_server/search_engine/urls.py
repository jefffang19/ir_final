from django.urls import path

from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('import_csv', views.import_csv, name = 'import_csv'),
    path('journal_list', views.journal_list, name = 'journal_list'),
]