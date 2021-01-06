import json

# for parsing xml file
from bs4 import BeautifulSoup
def xml_reader(path, target_tag):
    f = open(path,'r',encoding="utf-8")

    raw = f.read()
    soup = BeautifulSoup(raw, 'lxml')
    tags = soup.find_all(target_tag)

    # parse the abstract tag
    abstracts = []
    for abst in tags:
        AbstractText = abst.find_all('abstracttext')

        abstract_texts = ""

        for i in AbstractText:
            if i.get('label') != None:
                abstract_texts= abstract_texts + ' [' + i.get('label') + '] ' + i.string
            else:
                abstract_texts = abstract_texts + ' ' + i.string

        abstracts.append(abstract_texts)

    return abstracts

# tokenlize a string from xml and store as a array (len = number of articles)
# the element of array looks like
# { 'sentence' : 'I like apple',
#   'words' : ['I', 'like', 'apple']}
def xml_string_parser(raw):
    many_articles = []
    # many articles
    for raw_art in raw:
        # get rid of \n
        for n in range(len(raw_art)):
            if raw_art[n] == '\n':
                raw_art[n] == ' '
        d = {'sentence' : raw_art, 'words' : []}
    
        for i in range(len(d['sentence'].split(' '))):
            d['words'].append( [d['sentence'].split(' ')[i], i] )

        many_articles.append(d)

    return many_articles


# read a json file from path
def json_reader(path):
    input_file = open(path,'r')
    input_raw = input_file.read()
    input_json = json.loads(input_raw)
    
    return input_json

# parse a json file and store as a array (len = number of articles)
# the element of array looks like
# { 'sentence' : 'I like apple',
#   'words' : ['I', 'like', 'apple']}
def json_parser(json_dict, tag):
    result = []

    for i in json_dict:
        sentence = []
        for c in i[tag]:
            if(c.isascii()):
                sentence.append(c)
                
        sentence = ''.join(sentence)
        
        element = {}
        words = []
        pos = []
        element['sentence'] = sentence
        for j in range(len(sentence.split())):
            words.append( [sentence.split()[j], j] )
        element['words'] = words
        
        result.append(element)
    
    return result

def remove_puncuation(word_list):
    import string
    
    en_titles = ['Mr.', 'Mrs.', 'Dr.', 'Prof.','Hon.']

    for i in range(len(word_list)):
        if word_list[i][0] in en_titles:
            continue
        elif len(word_list[i][0])==2 and word_list[i][0][0].isupper():
            continue
        else:
            for j in string.punctuation:
                word_list[i][0] = word_list[i][0].replace(j, '')
       
    # remove blank string from the list
    word_list = [i for i in word_list if i[0] != ""]
    
    return word_list


def words_to_lower(word_list):
    return [ [i[0].lower(), i[1]] for i in word_list]


def remove_stopords(word_list, stopword_path = 'search_engine/stop_words.txt'):
    f = open(stopword_path)
    stop_words = f.read().split('\n')
    # now we create a new word set without the stop words
    words = [ [word_list[i][0], word_list[i][1]] for i in range(len(word_list)) if word_list[i][0] not in stop_words]
    
    return words


def stemming(word_list):
    from nltk.stem import PorterStemmer 

    ps = PorterStemmer() 

    for i in range(len(word_list)):
        word_list[i][0] = ps.stem(word_list[i][0])
        
    return word_list


# return type
# { 'sentence' : '\n I like apple',
#   'words' : [['I',1], ['like',2], ['apple',3]],
# }
def data_processor(input_path, mode = 'json', tag = 'p'):
    if mode == 'json':
        raw_json = json_reader(input_path)
        articles = json_parser(raw_json, tag)
        for i in articles:
            # process words list
            i['words'] = stemming(remove_stopords(words_to_lower(remove_puncuation(i['words']))))
        
        return articles

    elif mode == 'xml':
        abst = xml_reader(input_path, tag)

        many_articles = xml_string_parser(abst)

        new_many_articles = []
        for i in many_articles:
            i['words'] = stemming(remove_stopords(words_to_lower(remove_puncuation(i['words']))))
            new_many_articles.append(i)

        return new_many_articles


# parse the user input form into tokens
# return a list
def string_to_tokens(in_str):
    keywords = in_str.split()
    keywords = [[keywords[i], i] for i in range(len(keywords))]
    keywords = stemming(remove_stopords(words_to_lower(remove_puncuation(keywords))))
    return keywords


# handle a uploaded file to server
def handle_uploaded_file(f):
    with open('temp_uploaded', 'wb+') as dest:
        for chunk in f.chunks():
            dest.write(chunk)


def count_sent(abstract):
    import nltk
    temp = nltk.sent_tokenize(abstract)
    return len(temp)