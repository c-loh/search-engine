import os
import json
from bs4 import BeautifulSoup
import re
import nltk
# from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
# from nltk import tokenize
from collections import defaultdict
import Posting
import krovetz
import sys
import pickle
# from langdetect import detect
# import langdetect

def tokenize(token_file: str) -> [str]:
	try:
		token_list = []
		for line in token_file: # O(N)
			token_list += re.findall(r"[0-9a-zA-Z]{2,}", line.lower())
		return token_list
	except FileNotFoundError:
		print("File is not found. ")
	except UnicodeDecodeError:
		print("File contains invalid characters.")
	except TypeError:
		print("An error has occurred and the program has exited.")


def tokenizer(token_dict, loaded_json, doc_count) -> "return dictionary":
    
    # load text from json file
    # try:
    #     with open(filename, "r") as current_file:
    #         loaded_json = json.loads(current_file.read())
    # except UnicodeDecodeError:
    #     return token_dict
    
    soup2 = BeautifulSoup(loaded_json["content"], features="lxml")

    # stuff when considering weight
    title = soup2.find_all('title')
    if len(title) > 0:
        title = title[0].get_text().lower() #gives title of page
    else:
        title = ""
    bold = soup2.find_all('b')  # all bold?
    headers = soup2.find_all(re.compile('^h[1-6]$')) # all headers (including tags)
    # print("BOLD:", bold)

    # lowercase, get rid of punctuation, get casual tokenization w nltk
    soup2_text = soup2.get_text().lower()
    soup2_text = re.sub(r"\.[^a-z]|,|\(|\)|:|&|;|\?|!|\"|\{|\}|\[|\]", " ", soup2_text)
    # words = nltk.tokenize.casual_tokenize(soup2_text)
    words = tokenize(soup2_text)
    doc_word_count = len(words)
    # print("WORDS: ", words)

    # stem all words  
    # krovetz stemmer method
    words = stemmer(words)

    # # hash url into docID
    # docid = hash(loaded_json["url"]) 

    # print("WORDS: ", words)

    # {token: {docid: posting, docid2: posting, ...}, token2: {}, ...}
    for index in range(len(words)):
        if doc_count in token_dict[words[index]]:
            p = token_dict[words[index]][doc_count]
            p.incr_freq()
            p.positions.append(index) # index
        else:
            p = Posting.Posting(doc_word_count, loaded_json["url"])
            token_dict[words[index]][doc_count] = p
            p.incr_freq()
            p.positions.append(index)

    # consider bolded text, titles, headers
    token_dict = specialwords(token_dict, doc_count, bold, title, headers, doc_word_count, loaded_json["url"])
    
    return token_dict
    
# {token: {docid: posting, docid2: posting2, ...}, token2: {...}, ...}  

def offload_by_letter(d):
    # print("we offloading")
    sorted_keys = sorted(d)
    # print("sorted_keys: ", sorted_keys)
    if (len(sorted_keys) == 0):
        return
    
    i = 0
    curChar = sorted_keys[0][0]         # first character of first token (idk if this'll get that or another bit of data probably the latter tho rip)

    # nextChar = next_letter(curChar)
    nextChar = sorted_keys[i+1][0]
    
    tempDict = basic_load(curChar + ".txt")

    # {apricot, apple, bear, brown}

    while (i < len(sorted_keys)):    
        curChar = sorted_keys[i][0]
        if not curChar.isalnum() or not re.match(r"[0-9a-zA-Z]", curChar):
            i += 1
            continue
        
        # if its at the last letter
        if(i == len(sorted_keys)-1):
            basic_offload(curChar + ".txt", tempDict)       # offload to file
            tempDict = basic_load(curChar + ".txt")         # load the next letter file
            return

        nextChar = sorted_keys[i+1][0]                      # get the nextChar

        # if key already exists in file, update 
        if sorted_keys[i] in d:
            tempDict.update(d[sorted_keys[i]])
        # else add new to file
        else:
            tempDict[sorted_keys[i]] = d[sorted_keys[i]]

        if curChar != nextChar:
            print("we really really offloading at letter:", curChar)
            basic_offload(curChar + ".txt", tempDict)       # offload to file
            tempDict = basic_load(curChar + ".txt")         # load the next letter file

        # print(sorted_keys[i])
        i += 1
        
def basic_offload(filename, d):
    # open(filename, 'rb+')
    with open("index-files/" + filename, 'wb') as file:
        #print("dump dict:", d)
        pickle.dump(d, file)

def basic_load(filename):
    d = dict()

    try:
        with open("index-files/" + filename, 'rb+') as file:
            d = pickle.load(file)
            # print("pickle.load result:", d)
    except FileNotFoundError:
        return d
        
    return d

def stemmer(words):
    ks = krovetz.PyKrovetzStemmer()
    for w in range(len(words)):
       words[w] = ks.stem(words[w])
    return words


def specialwords(token_dict, docid, bold, title, headers, doc_word_count, url):
    # consider bolded text
    for b in bold:                              
        b = b.get_text().lower().split()
        for word in b:
            if word in token_dict and docid in token_dict[word]: 
                p = token_dict[word][docid]
            else:
                p = Posting.Posting(doc_word_count, url)
                token_dict[word][docid] = p
                p.incr_freq()
            p.incr_bold()
            
    # consider title
    for t in title.split():
        # p = Posting.Posting()
        if t in token_dict and docid in token_dict[t]:
            p = token_dict[t][docid]
        else:
            p = Posting.Posting(doc_word_count, url)
            token_dict[t][docid] = p
        p.incr_freq()
        p.incr_title()
    
    # consider header
    for h in headers:
        h = h.get_text().lower().split()
        for word in h:
            if word in token_dict and docid in token_dict[word]:
                p = token_dict[word][docid]
            else:
                p = Posting.Posting(doc_word_count, url)
                token_dict[word][docid] = p
                p.incr_freq()
            p.incr_header()
    
    return token_dict
        
if __name__ == "__main__":
    # filename = "DEV/aiclub_ics_uci_edu/8ef6d99d9f9264fc84514cdd2e680d35843785310331e1db4bbd06dd2b8eda9b.json"
    # filename = "DEV/archive_ics_uci_edu/0ae6e2b60c713688fd7ff3ba6ebfc2dc145576f0821c8a5b63f0273ffb90a20f.json"
    filename = ""
    nltk.download('wordnet')
    doc_count = 0
    token_dict = defaultdict(dict)
    # docMapping = dict() #keeps track of which docID belongs to which doc

    # testing single doc
    # try:
    #     with open(filename, "r") as current_file:
    #         loaded_json = json.loads(current_file.read())
    # except UnicodeDecodeError:
    #     pass
    # tokenizer(token_dict, loaded_json, 0)
    
    
    for direc in os.listdir("DEV"):
        for f in os.listdir("DEV/" + direc):
            filename = "DEV/" + direc + "/" + f
            try:
                with open(filename, "r") as current_file:
                    loaded_json = json.loads(current_file.read())
            except UnicodeDecodeError:
                continue

            token_dict = tokenizer(token_dict, loaded_json, doc_count)
            # print token_dict
            # for token in token_dict:
            #     print(token, ": {")
            #     for (doxcid,posting) in token_dict[token].items():
            #         print("  ", docid, ": positions=", posting.get_positions())
            #         # print("  ", docid, ": freq=", posting.get_freq(), ", bold=", posting.get_bold(), ", header=", posting.get_header(), ", title=", posting.get_title())
            #     print("}")  
            print("DOC_COUNT =", doc_count)   # cap it at 50,000 docs before offloading?
            # print("SIZE =", sys.getsizeof(token_dict))
            if(doc_count % 500 == 0):
                offload_by_letter(token_dict)
                token_dict.clear()
            # docMapping[doc_count] = loaded_json["url"]
            doc_count += 1
            # print("docMapping  ", docMapping)

    unique_tokens = 0
    total_size = 0

    for o in os.listdir("index-files"):
        total_size += os.path.getsize(o)
        d = basic_load(o)
        with open("posting_info.txt", "a") as pinfo:
            pinfo.write(o)
            pinfo.write("\n")
            pinfo.write("\n")
            for token in d:
                pinfo.write(token, d[token].url, d[token].score)
                pinfo.write("\n")
        unique_tokens += len(d)
        d.clear()

    
    print("DONE INFO: \n")
    print("number of documents:", doc_count+1)
    print("number of unique tokens:", unique_tokens)
    print("total size in KB:", total_size/1000)
    # {token: {docid: posting, docid2: posting2, ...}, token2: {...}, ...}  
    
    
    # print(sys.maxsize)
    # print(sys.getsizeof(token_dict))
