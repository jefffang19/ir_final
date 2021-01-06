from django.db import models

# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=200)
    abstract = models.CharField(max_length=200)

class Word(models.Model):
    context = models.CharField(max_length=200)
    position = models.ManyToManyField(Article)
    pos_in_a_article = models.IntegerField()

class StemFreq(models.Model):
    word = models.CharField(max_length=200)
    frequency = models.IntegerField()

class OriginFreq(models.Model):
    word = models.CharField(max_length=200)
    frequency = models.IntegerField()

class Tsne(models.Model):
    model_num = models.IntegerField()
    dataset_name = models.CharField(max_length=200)
    x_val = models.FloatField()
    y_val = models.FloatField()
    label = models.CharField(max_length=200)
    perplexity = models.IntegerField()

class Bmc(models.Model):
    title = models.CharField(max_length=200)
    subset = models.CharField(max_length=200)
    background = models.CharField(max_length=200)
    methods = models.CharField(max_length=200)
    results = models.CharField(max_length=200)
    conclusion = models.CharField(max_length=200)

class PositionInDoc(models.Model):
    article_id = models.IntegerField()
    position = models.IntegerField()
    origin_term = models.CharField(max_length=200)

class BsbiBlocks(models.Model):
    term = models.CharField(max_length=200)
    position = models.ManyToManyField(Article)
    pos_in_a_article = models.ManyToManyField(PositionInDoc)

class Bsbi(models.Model):
    term = models.CharField(max_length=200)
    pos_in_a_artcle = models.ManyToManyField(PositionInDoc)

class Spimi(models.Model):
    term = models.CharField(max_length=200)
    pos_in_a_artcle = models.ManyToManyField(PositionInDoc)