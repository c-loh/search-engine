import os
import json
from bs4 import BeautifulSoup
import re
import nltk
from nltk.tokenize import RegexpTokenizer
# from nltk import tokenize
from collections import defaultdict
import Posting
import krovetz
import sys
import pickle

class Milestone1:
    def __init__(self):
        filename = ""
        nltk.download('wordnet')
        doc_count = 0
        token_dict = defaultdict(dict)
        self.url_mapping = dict()
        
        for direc in os.listdir("DEV"):
            if (direc == ".DS_Store"):
                continue
            for f in os.listdir("DEV/" + direc):
                filename = "DEV/" + direc + "/" + f
                try:
                    with open(filename, "r") as current_file:
                        loaded_json = json.loads(current_file.read())
                except UnicodeDecodeError:
                    continue
                    
                token_dict = self.tokenizer(token_dict, loaded_json, doc_count)

                if(doc_count % 20000 == 0):
                    self.offload_by_letter(token_dict)
                    token_dict.clear()

                doc_count += 1
        
        # offload everything else leftover at the end
        self.offload_by_letter(token_dict)

        unique_tokens = 0
        total_size = 0

        for o in os.listdir("index-files"):
            total_size += os.path.getsize("index-files/"+o)
            d = self.basic_load(o)
            with open("posting_info.txt", "a") as pinfo:
                pinfo.write(o)
                pinfo.write("\n")
                for token in d:
                    pinfo.write(token)
                    pinfo.write("\n")
                    for doc in d[token]:
                        pinfo.write(" url: ")
                        pinfo.write(str(d[token][doc].get_url()))
                        pinfo.write(" score: ")
                        pinfo.write(str(d[token][doc].compute_score()))
                        pinfo.write("\n")
                pinfo.write("\n")
                pinfo.write("\n")
            unique_tokens += len(d)
            d.clear()

        
        print("DONE INFO: \n")
        print("number of documents:", doc_count)
        print("number of unique tokens:", unique_tokens)
        print("total size in KB:", total_size/1000)

        # pickle dump url_mapping so we can use it in search !
        with open("url_mapping.txt", 'wb') as file:
            pickle.dump(self.url_mapping, file)


    # def tokenize(self, token_file: str) -> [str]:
    #     try:
    #         token_list = []
    #         for line in token_file: # O(N)
    #             token_list += re.findall(r"[0-9a-zA-Z]{2,}", line.lower())
    #         return token_list
    #     except FileNotFoundError:
    #         print("File is not found. ")
    #     except UnicodeDecodeError:
    #         print("File contains invalid characters.")
    #     except TypeError:
    #         print("An error has occurred and the program has exited.")

    def tokenizer(self, token_dict, loaded_json, doc_count) -> "return dictionary":
        # create soup from url
        soup2 = BeautifulSoup(loaded_json["content"], features="lxml")

        # stuff when considering weight
        title = soup2.find_all('title')
        if len(title) > 0:
            title = title[0].get_text().lower() #gives title of page
        else:
            title = ""
        bold = soup2.find_all('b')  # all bold?
        headers = soup2.find_all(re.compile('^h[1-6]$')) # all headers (including tags)

        # lowercase, get rid of punctuation, get casual tokenization w nltk
        soup2_text = soup2.get_text().lower()
        soup2_text = re.sub(r"[^a-z0-9]", " ", soup2_text)
        # words = self.tokenize(soup2_text)
        words = nltk.tokenize.casual_tokenize(soup2_text)

        doc_word_count = len(words)

        # stem all words  
        words = self.stemmer(words)

        # {token: {docid: posting, docid2: posting, ...}, token2: {}, ...}
        for index in range(len(words)):
            # doc_count is same as docid
            if doc_count in token_dict[words[index]]:
                p = token_dict[words[index]][doc_count]
                p.incr_freq()
                p.positions.append(index) # index
            else:
                p = Posting.Posting(doc_word_count, loaded_json["url"])
                self.url_mapping[doc_count] = loaded_json["url"]
                token_dict[words[index]][doc_count] = p
                p.incr_freq()
                p.positions.append(index)

        # consider bolded text, titles, headers
        token_dict = self.specialwords(token_dict, doc_count, bold, title, headers, doc_word_count, loaded_json["url"])
        
        return token_dict
        
    # {token: {docid: posting, docid2: posting2, ...}, token2: {...}, ...}  

    def offload_by_letter(self, d):
        # print("we offloading")
        sorted_keys = sorted(d)
        # print("sorted_keys: ", sorted_keys)
        if (len(sorted_keys) == 0):
            return
        
        i = 0
        curChar = sorted_keys[0][0]         # first character of first token (idk if this'll get that or another bit of data probably the latter tho rip)
        nextChar = sorted_keys[i+1][0]
        
        tempDict = self.basic_load(curChar + ".txt")

        # {apricot, apple, bear, brown}

        while (i < len(sorted_keys)):    
            curChar = sorted_keys[i][0]
            if not curChar.isalnum() or not re.match(r"[0-9a-zA-Z]", curChar):
                i += 1
                continue
            
            # if its at the last letter
            if(i == len(sorted_keys)-1):
                self.basic_offload(curChar + ".txt", tempDict)       # offload to file
                tempDict = self.basic_load(curChar + ".txt")         # load the next letter file
                return

            nextChar = sorted_keys[i+1][0]                      # get the nextChar

            # if key already exists in file, update 
            if sorted_keys[i] in tempDict:
                tempDict[sorted_keys[i]].update(d[sorted_keys[i]])
            # else add new to file
            else:
                tempDict[sorted_keys[i]] = d[sorted_keys[i]]

            if curChar != nextChar:
                # print("we really really offloading at letter:", curChar)
                self.basic_offload(curChar + ".txt", tempDict)       # offload to file
                tempDict = self.basic_load(nextChar + ".txt")         # load the next letter file

            # print(sorted_keys[i])
            i += 1
        
    def basic_offload(self, filename, d):
        # open(filename, 'rb+')
        with open("index-files/" + filename, 'wb') as file:
            #print("dump dict:", d)
            pickle.dump(d, file)

    def basic_load(self, filename):
        d = dict()
        try:
            with open("index-files/" + filename, 'rb+') as file:
                try:
                    d = pickle.load(file)
                except pickle.UnpicklingError:
                    return d
                # print("pickle.load result:", d)
                # for token in d:
                #     print(token)
        except FileNotFoundError:
            return d
            
        return d

    def stemmer(self, words):
        ks = krovetz.PyKrovetzStemmer()
        for w in range(len(words)):
            words[w] = ks.stem(words[w])
        return words

    def specialwords(self, token_dict, docid, bold, title, headers, doc_word_count, url):
        # consider bolded text
        for b in bold:                              
            b = b.get_text().lower().split()
            for word in b:
                if word in token_dict and docid in token_dict[word]: 
                    p = token_dict[word][docid]
                else:
                    p = Posting.Posting(doc_word_count, url)
                    self.url_mapping[docid] = url
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
                self.url_mapping[docid] = url
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
                    self.url_mapping[docid] = url
                    token_dict[word][docid] = p
                    p.incr_freq()
                p.incr_header()
        
        return token_dict   