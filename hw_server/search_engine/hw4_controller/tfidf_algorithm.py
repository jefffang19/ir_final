from ..models import Bmc

def tfidf(query_word, method_tf, method_idf, subset):
    # get the docs
    bmc = ''
    if subset == 0:
        bmc = Bmc.objects.filter(subset = 'colorectal_cancer')
    elif subset == 1:
        bmc = Bmc.objects.filter(subset = 'genetic_disease')
    else:
        assert "Wrong Subset Error"

    bmc = list(bmc)

    doc_weight = []

    for i in range(len(bmc)):
        doc_weight.append( [bmc[i].title, tf(query_word, i, method_tf, bmc)*idf(query_word, method_idf, bmc), len(bmc[i].background.split(' '))+len(bmc[i].methods.split(' '))+len(bmc[i].results.split(' '))+len(bmc[i].conclusion.split(' '))] )


    return doc_weight

# create vector
def tfidf_vec(queryword, method_tf, method_idf, subset):
    # get the docs
    bmc = ''
    if subset == 0:
        bmc = Bmc.objects.filter(subset = 'colorectal_cancer')[:100]
    elif subset == 1:
        bmc = Bmc.objects.filter(subset = 'genetic_disease')[:100]
    else:
        assert "Wrong Subset Error"

    bmc = list(bmc)

    d_lens = [len(queryword.split(' '))]
    titles = [queryword]
    corpus = [queryword]
    corpus_bg = [queryword]
    corpus_mt = [queryword]
    corpus_rt = [queryword]
    corpus_con = [queryword]
    for i in bmc:
        s = '{} {} {} {}'.format(i.background, i.methods, i.results, i.conclusion)
        titles.append(i.title)
        d_lens.append(len(s.split(' ')))
        corpus.append(s)
        corpus_bg.append(i.background)
        corpus_mt.append(i.methods)
        corpus_rt.append(i.results)
        corpus_con.append(i.conclusion)

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    use_idf = True
    smooth_idf = False
    sublinear = False
    if method_idf == 0:
        use_idf = True
    elif method_idf == 1:
        use_idf = False
    else:
        smooth_idf = False
    if method_tf == 2:
        sublinear = True

    tfidf_vec = TfidfVectorizer(use_idf=use_idf, smooth_idf=smooth_idf, sublinear_tf=sublinear)
    tfidf_matrix = tfidf_vec.fit_transform(corpus)

    tfidf_bg_matrix = tfidf_vec.fit_transform(corpus_bg)
    tfidf_mt_matrix = tfidf_vec.fit_transform(corpus_mt)
    tfidf_rt_matrix = tfidf_vec.fit_transform(corpus_rt)
    tfidf_con_matrix = tfidf_vec.fit_transform(corpus_con)

    # return [cosine_similarity(tfidf_matrix.toarray()[0].reshape(1, -1), tfidf_matrix.toarray()[1].reshape(1, -1))]
    return tfidf_matrix.toarray(), titles, d_lens, tfidf_bg_matrix.toarray(), tfidf_mt_matrix.toarray(), tfidf_rt_matrix.toarray(), tfidf_con_matrix.toarray()

def cos_sim(matrix):
    from sklearn.metrics.pairwise import cosine_similarity
    c = []
    for i in range(len(matrix)):
        c.append(cosine_similarity(matrix[0].reshape(1, -1), matrix[i].reshape(1, -1))[0, 0] )

    return c

def cos_sim_para(q, tfidf_bg_matrix, tfidf_mt_matrix, tfidf_rt_matrix, tfidf_con_matrix):
    from sklearn.metrics.pairwise import cosine_similarity
    c = [0]
    max = -999
    for i in range(1, len(tfidf_bg_matrix)):
        pos = 0
        val = cosine_similarity(tfidf_bg_matrix[0].reshape(1, -1), tfidf_bg_matrix[i].reshape(1, -1))[0, 0]
        if val > max:
            max = val
            pos = 0
        val = cosine_similarity(tfidf_mt_matrix[0].reshape(1, -1), tfidf_mt_matrix[i].reshape(1, -1))[0, 0]
        if val > max:
            max = val
            pos = 1
        val = cosine_similarity(tfidf_rt_matrix[0].reshape(1, -1), tfidf_rt_matrix[i].reshape(1, -1))[0, 0]
        if val > max:
            max = val
            pos = 2
        val = cosine_similarity(tfidf_con_matrix[0].reshape(1, -1), tfidf_con_matrix[i].reshape(1, -1))[0, 0]
        if val > max:
            max = val
            pos = 3

        c.append(pos)

    return c

def tf(query_word, doc_n, method, bmc):
    _ftd = ftd(query_word, bmc)
    # raw count
    if method == 0:
        return _ftd[doc_n]['ftd']
    # term frequency
    elif method == 1:
        return _ftd[doc_n]['ftd'] / _ftd[doc_n]['words_cnt']
    # log normalization
    elif method == 2:
        import math
        return math.log(1 + _ftd[doc_n]['ftd'])


def idf(query_word, method, bmc):
    import math
    _nt, _N = nt(query_word, bmc)
    # inverse document frequency
    if method == 0:
        # fix division by zero
        if _nt == 0:
            return 0
        else:
            if math.log(_N/_nt) < 0:
                print("{} {}".format(_N, _nt))
            return math.log(_N/_nt)
    # unary
    elif method == 1:
        return 1
    # inverse document frequency smooth
    elif method == 2:
        return math.log(_N/(_nt+1)) + 1


# definition of ftd and nt, please look at td-idf English Wiki page

def ftd(query_word, bmc):
    articles = [i for i in bmc]

    # Freq(t,d)
    # a array frequncey of query term in each documents
    # element is dictionary
    f_td = []

    for doc in articles:
        temp_ftd = {}
        query_word_cnt = 0
        all_words_cnt = 0
        for paragraph in [doc.background, doc.methods, doc.results, doc.conclusion]:
            for word in paragraph.split(' '):
                all_words_cnt += 1
                if word == query_word:
                    query_word_cnt += 1

        # temp_ftd['title'] = doc.title
        temp_ftd['ftd'] = query_word_cnt
        temp_ftd['words_cnt'] = all_words_cnt
        f_td.append(temp_ftd)

    return f_td

# return nt, N
def nt(query_word, bmc):
    articles = [i for i in bmc]

    # query term exist in how many document
    _nt = 0
    # document count
    N = len(articles)

    for doc in articles:
        t_exist = False
        for paragraph in [doc.background, doc.methods, doc.results, doc.conclusion]:
            for word in paragraph.split(' '):
                if word == query_word:
                    if not t_exist:
                        _nt += 1
                        t_exist = True
                        break

            if t_exist:
                break

    return _nt, N