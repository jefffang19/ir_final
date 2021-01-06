def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches

def parse_mesh_func():
    mesh = open('../c2020.bin')

    # read covid-19 related NM
    f = open('../mesh_nm')
    _covid_term = f.readlines()
    # remove newline
    covid_term = []
    for i in range(len(_covid_term) - 1):
        covid_term.append(_covid_term[i][:-1])

    covid_term.append(_covid_term[len(_covid_term) - 1])

    # deal with the first line
    line = mesh.readline()

    # word : [Synonyms]
    index = {}

    # Synonym : word
    inverted_index = {}

    _index = ''
    while line:
        line = mesh.readline()
        if line == '*NEWRECORD\n':
            _index = ''
        elif line[:2] == 'NM' and line[:5] != 'NM_TH':
            # print(line, end='')
            _index = line[5:-1]
            #         print(_index)

            # create a synonyms index
            # add oneself to its synonyms
            index[_index] = [_index]

        elif line[:2] == 'SY':
            # print(line, end='')

            # append to synonyms index
            index[_index].append(line[5:].split('|')[0])
            # create a inverted index
            inverted_index[line[5:].split('|')[0]] = _index

    # return index, inverted_index

    # filter out words without covid19
    # filter out words without covid19
    filt_index = {}
    for i in index.keys():
        if i in covid_term:
            filt_index[i] = index[i]

    filt_inv_index = {}
    for i in filt_index.keys():
        for j in filt_index[i]:
            filt_inv_index[j] = i

    return filt_index, filt_inv_index

# return dictionary of each term and corresponding freq
def create_mesh_spell_check_dict():
    from ..models import Bsbi, Spimi, PositionInDoc

    raw = PositionInDoc.objects.all()

    mesh_freq = {}

    for i in raw:
        if i.origin_term not in mesh_freq.keys():
            mesh_freq[i.origin_term] = 1
        else:
            mesh_freq[i.origin_term] += 1

    return mesh_freq

# spell checking function using mesh dictionary
# return correct form
def mesh_spell_check(term):
    mis_spell = False

    from spellchecker import SpellChecker

    # turn off loading a built language dictionary, case sensitive on
    spell = SpellChecker(language=None, case_sensitive=True)

    # load dictionary
    spell.word_frequency.load_dictionary('spellcheck_dict.json')

    # check if not misspell
    if term in spell:
        return mis_spell, term

    # if misspell
    return True, spell.correction(term)
