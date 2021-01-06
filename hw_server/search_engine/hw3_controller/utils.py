from ..models import Word

# return 1 dict and 1 list
# list => article with stemmed words
# dict => stemmed words : its frequency
def get_subset(keyword):
    from search_engine.parsing_utils import string_to_tokens
    corrected_keyword = keyword

    # query for the data subset
    keywords_cleaned = string_to_tokens(corrected_keyword)
    articles_pk = []  # get the target articles' pk

    for i in keywords_cleaned:
        w = Word.objects.filter(context=i[0])

        for j in w:
            mode = j.position.get()
            # append article pk
            if mode.pk not in articles_pk:
                articles_pk.append(mode.pk)

    words_freq = {}
    words = []
    # get the target articles' words
    for i in articles_pk:
        w = Word.objects.filter(position__id=i)
        for j in w:
            if j.context not in words_freq.keys():
                words_freq[j.context] = 1
            else:
                words_freq[j.context] += 1
            words.append(j.context)

    # sort the dict by value
    words_freq = {k: v for k, v in sorted(words_freq.items(), key=lambda item: item[1], reverse=True)}

    return words_freq, words

def stemmed(keyword):
    from search_engine.parsing_utils import string_to_tokens
    keywords_cleaned = string_to_tokens(keyword)

    for i in keywords_cleaned:
        return i[0]