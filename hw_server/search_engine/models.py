from django.db import models

# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=200)
    abstract = models.CharField(max_length=500)
    cancer = models.CharField(max_length=200)
    mirna = models.CharField(max_length=200)
    journal = models.CharField(max_length=200)
    impact_factor = models.FloatField()

class Mirna(models.Model):
    name = models.CharField(max_length=200)

class MirnaFamily(models.Model):
    name = models.CharField(max_length=200)
    root = models.ForeignKey(Mirna, on_delete=models.CASCADE)

class Cancer(models.Model):
    name = models.CharField(max_length=200)

class Sentence(models.Model):
    sent = models.CharField(max_length=200)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    mirna = models.ManyToManyField(MirnaFamily)
    cancer = models.ManyToManyField(Cancer)
