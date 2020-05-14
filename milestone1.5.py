# ADDITIONAL PROCESSING STEPS DONE AFTER MILESTONE ONE BUT NOT NECESSARILY 
# DONE IN MILESTONE 2.

import os
import milestone1
import pickle

pos_index = dict()

def basic_load(filename):
    d = dict()
    try:
        with open("index-files/" + filename, 'rb+') as file:
            try:
                d = pickle.load(file)
            except pickle.UnpicklingError:
                return d
    except FileNotFoundError:
        return d
    return d

def basic_offload(filename, d):
    # open(filename, 'rb+')
    with open(filename, 'wb') as file:
        #print("dump dict:", d)
        pickle.dump(d, file)


for o in os.listdir("index-files"):
    d = basic_load(o)
    # d = basic_load("a.txt")
    line_num = 1
    # print("d:", d)
    with open ("formatted-files/" + str(o[0])+ "_format.txt", "w") as filename:
    # with open ("formatted-files/a_format.txt", "w") as filename:
        sorted_keys = sorted(d)
        for token in sorted_keys:
            pos_index[token] = line_num+1
            filename.write(token)
            filename.write('\n')
            # docid/score/1/3/17/85/*docid/score/positions*
            sorted_postings = dict()
            for docid, posting in d[token].items():
                sorted_postings[docid] = posting.compute_score()
            # sorting by score
            for doc in sorted(sorted_postings, key=lambda x: -sorted_postings[x]):
                filename.write(str(doc))
                filename.write("/")
                filename.write(str(sorted_postings[doc]))   # score
                filename.write('/')
                for pos in d[token][doc].get_positions():
                    filename.write(str(pos))
                    filename.write('/')
                filename.write('*')
                # write info all formatted on one line
            filename.write('\n')
            line_num += 2
            # split by *
            # ['docid/score/1/3/17/85', 'docid/score/positions]
            # split each of those by / when necessary
            # ['docid', 'score', '1', '3', '17', '85', '']

basic_offload("pos_index.txt", pos_index)
            

            
