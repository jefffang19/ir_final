from django.http import HttpResponse, JsonResponse
from ..models import Word
from .utils import get_subset, stemmed

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_model(request):
    from gensim.models.word2vec import Word2Vec

    if request.method == 'GET':

        w = Word.objects.all()

        words = []

        for i in w:
            # check if is English words
            if i.context.isascii():
                words.append(i.context)

        words = [words]

        # word2vector
        model = Word2Vec(words, size=100, window=5, min_count=1, compute_loss=True, workers=4, sg=1)
        # training_loss = model.get_latest_training_loss()
        # print(training_loss)
        model.save("word2vec_sg.model")

        return HttpResponse("Model created")

    else:
        keyword = request.POST['keyword']

        _, words = get_subset(keyword)
        words = [words]

        # word2vector
        model = Word2Vec(words, size=100, window=3, min_count=1, compute_loss=True, workers=4, sg=1)
        # training_loss = model.get_latest_training_loss()
        # print(training_loss)
        model.save("word2vec_{}_sg.model".format(keyword))

        return HttpResponse("{} Model created".format(keyword))

@csrf_exempt
def test_model_similar(request):
    from gensim.models.word2vec import Word2Vec

    if request.method == 'POST':
        keyword = request.POST['keyword']
        model = Word2Vec.load("word2vec_{}_sg.model".format(keyword))

        from .use_model import most_similar
        most_similar(model, ['ct', stemmed(keyword)], 2000).to_csv("word2vec_{}.csv".format(keyword))

        # get cosine similarity ranking
        import pandas as pd
        df = pd.read_csv('word2vec_{}.csv'.format(keyword))
        pos = df[df[stemmed(keyword)] == 'ct'].index.values.astype(int)[0]

        return JsonResponse({
            'cos_sim': str(model.wv.similarity('ct', stemmed(keyword))),
            'vocab len': str(len(model.wv.vocab)),
            'rank': str(pos),
        })
    else:
        model = Word2Vec.load("word2vec_sg.model")

        from .use_model import most_similar
        most_similar(model, ['ct', 'covid19'], 2000).to_csv("word2vec.csv")

        return JsonResponse({
            'cos_sim': str(model.wv.similarity('ct', 'imag')),
            'vocab len': str(len(model.wv.vocab)),
        })
