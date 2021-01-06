from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from ..models import Word, StemFreq, Tsne

import pandas as pd

from tsnecuda import TSNE
import numpy as np  # array handling

from django.views.decorators.csrf import csrf_exempt


def use_model(request, set=0, perplexity=30):
    from gensim.models.word2vec import Word2Vec
    from .utils import stemmed

    model = Word2Vec.load("word2vec_sg.model")
    keyword = "covid19"
    if set == 1:
        model = Word2Vec.load("word2vec_image_sg.model")
        keyword = "image"
    elif set == 2:
        model = Word2Vec.load("word2vec_mask_sg.model")
        keyword = "mask"

    # print(type(model.wv.most_similar(keyword, topn=100)))
    # most_similar(model, ['china', 'mask', 'covid19'], 100).to_csv("word2vec.csv")
    # print(model.wv.similarity('covid19', 'covid19'))

    # get all label and (x,y)
    x_vals, y_vals, labels = tsne(perplexity, model)

    # create zipf data
    words, freqs = create_zipf(set)

    # define high, mid, low frequency
    HIGH_FREQ = 100  # [0, 100)
    MID_FREQ = 1000  # [100, 1000)
    # low freq [1000,)

    # prepare template render data
    d = template_data(x_vals, y_vals, labels, words, HIGH_FREQ, MID_FREQ)

    return_dict = {
        'high_freq': [0,HIGH_FREQ],
        'mid_freq': [HIGH_FREQ, MID_FREQ],
        'low_freq': [MID_FREQ, len(x_vals)],
        'freqs': freqs,
        'cos_sim': str(model.wv.similarity('ct', stemmed(keyword))),
        'n95': str(model.wv.similarity('n95', stemmed(keyword))),
        'subset_name': keyword,
        'most_sim': model.wv.most_similar(stemmed(keyword), topn=10),
    }

    return_dict = {**return_dict, **d}

    # print(return_dict.keys())

    # plot_with_matplotlib(x_vals, y_vals, labels, top_words)

    return render(request, 'search_engine/w2v_tsne.html', return_dict)


def tsne(perplexity, model):
    from gensim.models.word2vec import Word2Vec

    x_vals, y_vals, labels = reduce_dimensions(model, perplexity)

    return x_vals, y_vals, labels


def most_similar(w2v_model, words, topn=10):
    similar_df = pd.DataFrame()
    for word in words:
        try:
            similar_words = pd.DataFrame(w2v_model.wv.most_similar(word, topn=topn), columns=[word, 'cos'])
            similar_df = pd.concat([similar_df, similar_words], axis=1)
        except:
            print(word, "not found in Word2Vec model!")
    return similar_df


def reduce_dimensions(model, perplexity):
    num_dimensions = 2  # final num dimensions (2D, 3D, etc)

    vectors = []  # positions in vector space
    labels = []  # keep track of words to label our data again later
    for word in model.wv.vocab:
        vectors.append(model.wv[word])
        labels.append(word)

    # convert both lists into numpy vectors for reduction
    vectors = np.asarray(vectors)
    labels = np.asarray(labels)

    # reduce using t-SNE
    vectors = np.asarray(vectors)
    tsne = TSNE(n_components=num_dimensions, perplexity=perplexity)
    vectors = tsne.fit_transform(vectors)

    x_vals = [v[0] for v in vectors]
    y_vals = [v[1] for v in vectors]

    print(x_vals[:5])
    return x_vals, y_vals, labels


def plot_with_matplotlib(x_vals, y_vals, labels, draw_words):
    import matplotlib.pyplot as plt
    import random

    random.seed(0)

    plt.figure(figsize=(12, 12))
    plt.scatter(x_vals, y_vals)

    #
    # Label draw_words[]
    #
    selected_indices = []
    for i in range(len(labels)):
        if labels[i] in draw_words:
            selected_indices.append(i)

    for i in selected_indices:
        plt.annotate(labels[i], (x_vals[i], y_vals[i]))

    plt.savefig('model_fig.png')


# return words list and freq list
def create_zipf(set):
    from .utils import get_subset

    words = []
    freq = []

    if set == 0:
        a = StemFreq.objects.all()
        for i in a:
            words.append(i.word)
            freq.append(i.frequency)

    elif set == 1:
        wf, w = get_subset('image')
        words = list(wf.keys())
        freq = list(wf.values())

    elif set == 2:
        wf, w = get_subset('mask')
        words = list(wf.keys())
        freq = list(wf.values())


    return words, freq

# return tsne data store in db
# return : x, y, labels
def get_tsne_data():
    tsne = Tsne.objects.filter(model_num=0)

    x_vals = []
    y_vals = []
    labels = []
    for i in tsne:
        x_vals.append(i.x_val)
        y_vals.append(i.y_val)
        labels.append(i.label)

    return x_vals, y_vals, labels

# return data to render in template
# return (dict): x_val, y_val
# args: x_vals, y_vals, labels => get from get_tsbe_data()
# args: words => from Stemfreq Model
# args: hf, mf => High Frequency, Mid Frequency
# args: name => prefix of return dict's key
def template_data(x_vals, y_vals, labels, words, hf, mf):
    high_label = []
    high_x = []
    high_y = []
    mid_label = []
    mid_x = []
    mid_y = []
    low_label = []
    low_x = []
    low_y = []
    for cnt, w in enumerate(labels):
        # high freq
        if w in words[:hf]:
            high_label.append(cnt)
            high_x.append(x_vals[cnt])
            high_y.append(y_vals[cnt])
        elif w in words[hf:mf]:
            mid_label.append(cnt)
            mid_x.append(x_vals[cnt])
            mid_y.append(y_vals[cnt])
        else:
            low_label.append(cnt)
            low_x.append(x_vals[cnt])
            low_y.append(y_vals[cnt])

    return_dict = {
      "x": high_x + mid_x + low_x,
      "y": high_y + mid_y + low_y,
    }

    return return_dict