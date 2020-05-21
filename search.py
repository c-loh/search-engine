import time
import nltk
import re
import krovetz
import pickle
import Posting
import linecache
from collections import defaultdict

# split query into words --> tokenize
# go to text file of first letter of each word
# see if word is in that file/dict
'''
tokenize query
results = find all docs where first word of query appears
for all remaining words in query:
    open respective text file
    see if word is in there
        if so, compare docIDs with what's in results currently
        and modify to contain only docs that are in both dicts
'''


'''
query = []
words = tokenize(query)
first_word = words[0]

results = dict()   # our function returns this
curchar = first_word[0]   # get first letter of token
dict = load(curchar + ".txt")    # go to appropriate letter index
if first_word in dict:
    for docid, posting in dict[first_word]:
        results[docid] = posting.get_score()nt
    // results = {docid: posting, docid: posting}
else:
    // the algorithm is over. no results found ??
    return None


for word in words[1:]:    # word is a token
    # tempDict = dict{}
    curchar = word[0]
    dict = basic_load(curchar + ".txt") # get function from ms1
    tempResults = dict{}
    for docid, posting in dict:
        if docid in results:
            tempResults[docid] = posting.get_score()
    results = tempResults

return sorted(results, key=lambda x: results[x])

'''
def basic_load(filename):
    d = dict()
    try:
        with open(filename, 'rb+') as file:
            try:
                d = pickle.load(file)
            except pickle.UnpicklingError:
                return d
    except FileNotFoundError:
        return d
        
    return d

def stemmer(words):
    ks = krovetz.PyKrovetzStemmer()
    for w in range(len(words)):
        words[w] = ks.stem(words[w])
    return words


def search(query, pos_index, cache_dict):
    # get input from console/python shell
    # query = input("Enter a query: ")

    start = time.time()

    # lowercase, get rid of punctuation, get casual tokenization w nltk
    query_text = query.lower()
    query_text = re.sub(r"\.[^a-z]|,|\(|\)|:|&|;|\?|!|\"|\{|\}|\[|\]", " ", query_text)
    words = nltk.tokenize.casual_tokenize(query_text)
    words = list(set(stemmer(words)))

    # data structures we need
    url_mapping = basic_load("url_mapping.txt")
    results = defaultdict(float)   # our function returns this

    # get the first word. results represents all ANDed urls but will start with all urls that have first_word in query 
    first_word = words[0]
    curchar = first_word[0]   # get first letter of token

    # FIRST WORD. 
    if first_word in cache_dict:
        line = cache_dict[first_word]
        results = first_posting(line, results)
    elif first_word in pos_index:
        charfile = "formatted-files/" + curchar + "_format.txt"
        # with open("formatted-files/" + curchar + "_format.txt", 'a') as charfile:
        # gets the posting list for token first_word
        line = linecache.getline(charfile, pos_index[first_word])
        results = first_posting(line, results)
        # split by *
        # ['docid/score/1/3/17/85', 'docid/score/positions]
    else:
        print("couldn't find first word:", first_word)
        return
        
        
    # deal with the rest of the words in the query
    for word in words[1:]:    # word is a token
        if word in cache_dict:
            line = cache_dict[word]
            tempResults = other_posting(line, results)
            results = tempResults
            
        elif word in pos_index:
            curchar = word[0]
            charfile = "formatted-files/" + curchar + "_format.txt"
            # with open("formatted-files/" + curchar + "_format.txt", 'a') as charfile:
            line = linecache.getline(charfile, pos_index[word])
            tempResults = other_posting(line, results)

            results = tempResults
        else:
            # if word is not in pos_index, then we can't really do anything
            print("couldn't find word:", word)
            return
    
    end = time.time()
    print('query time: ', end - start)

    real_results = dict()
    
    count = 0
    # print("number of results: ", len(results))
    for result in sorted(results, key=lambda x: results[x], reverse=True):
        url = url_mapping[int(result)]
        print(url, ":", results[result])
        real_results[url] = results[result]
        count += 1
        if count == 5:
            break
    
    return (real_results, end-start)
        

def cache_words(pos_index, cache_dict):
    cache_list = {'cristina', 'lopes', 'machine', 'learning', 'ACM', 'master', 'of', 'software', 'engineering', 'the', 'for', 'computer', 'science', 'and', 'but', 'UCI', 'or', 'not', 'to', 'thornton', 'shindler', 'pattis', 'ibrahim', 'ziv'}
    for word in cache_list:
        if word in pos_index:
            curchar = word[0]
            charfile = "formatted-files/" + curchar + "_format.txt"
            line = linecache.getline(charfile, pos_index[word])
            cache_dict[word] = line

def first_posting(line, results):
    postings = line.split('*')
    # ["docid/score/pos/pos/...", "docid/score/pos/pos/...", ...]
    # print("first word results:")
    for post in postings[:-1]:
        # split each of those by / when necessary
        # ['docid', 'score', '1', '3', '17', '85', '']
        post = post.split('/')
        # print("post: ", post)
        docid = post[0]
        # print(docid, ",")
        score = post[1]
        results[docid] += float(score)
    return results

def other_posting(line, results):
    tempResults = defaultdict(float)
    postings = line.split('*')
    # print("postings", postings)
    
    # print("second word results:")
    for post in postings[:-1]:
        # split each of those by / when necessary
        # ['docid', 'score', '1', '3', '17', '85', '']
        post = post.split('/')
        # print("post:", post)
        docid = post[0]
        # print(docid, ",")
        score = post[1]
        if docid in results:
            # print("docid found for second word:", docid)
            tempResults[docid] += float(score)
    return tempResults

def run(query):
    pos_index = basic_load("pos_index.txt")
    cache_dict = dict()
    cache_words(pos_index, cache_dict)
    return search(query, pos_index, cache_dict)

if __name__ == "__main__":
    # results = search()
    # pos_index = basic_load("pos_index.txt")
    # cache_dict = dict()
    # cache_words(pos_index, cache_dict)
    # search(pos_index, cache_dict)
    run("computer graphics")