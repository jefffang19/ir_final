# Generated by Django 3.1.1 on 2020-09-28 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_engine', '0003_word_pos_in_a_article'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='articleId',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='label',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
    ]
