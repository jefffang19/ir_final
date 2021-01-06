from ..forms import WordForm
from django.shortcuts import render
from ..models import StemFreq, OriginFreq

# hw 2 main template
def zipf(request, opt=0):
    form = WordForm()
    a = 'temp'
    title = 'temp'

    if opt == 0 or opt == 1:
        if opt == 0:
            a = OriginFreq.objects.all()
            title = 'Original'
        elif opt == 1:
            a = StemFreq.objects.all()
            title = 'Stemming'

        top100_words = []
        freq = []
        # other_words = []
        # other_freq = []

        count = 0
        for i in a:
            if count < 100:
                top100_words.append(i.word)
            
            freq.append(i.frequency)
            
            count += 1

        return render(request, 'search_engine/chart.html', {'title' : title, 'form' : form, 'top_words' : top100_words, 'freq' : freq, 'top_words_ori' : [], 'top_words_stem' : [], 'freq_ori' : [], 'freq_stem' : [] })
    elif opt == 2:
        title = 'Both'

        a1 = OriginFreq.objects.all()
        a2 = StemFreq.objects.all()

        top100_words_ori = []
        freq_ori = []
        top100_words_stem = []
        freq_stem = []

        count = 0
        for i in a1:
            if count < 100:
                top100_words_ori.append(i.word)
            
            freq_ori.append(i.frequency)
            
            count += 1

        count = 0
        for i in a2:
            if count < 100:
                top100_words_stem.append(i.word)
            
            freq_stem.append(i.frequency)
            
            count += 1

        return render(request, 'search_engine/chart.html', {'title' : title, 'form' : form, 'top_words_ori' : top100_words_ori, 'top_words_stem' : top100_words_stem, 'freq_ori' : freq_ori, 'freq_stem' : freq_stem, 'top_words' : [], 'freq' : [] })
        
