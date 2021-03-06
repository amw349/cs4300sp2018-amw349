from parsers_and_TFidf_setup import *
from numpy import linalg as LA
from scipy.sparse.linalg import svds
from sklearn.preprocessing import normalize
import csv
import os
import numpy as np

good_tags={}
# dict has keys = goodtag and values equal to list where the elements are avglikes, likescore, and totalposts

# with open("goodwords.csv") as f:
#     mycsv = csv.reader(f, delimiter = ",")
#     for x, row in enumerate(mycsv):
#         if x!=0:
#             good_tags[row[0]] = [float(row[1]), float(row[2]), float(row[3])]

def get_avglikes(tag):
    return mydict[tag][0]

def get_likescore(tag):
    val = float(mydict[tag][1])
    if val > 1:
        return float(val-1)*1.0
    elif val < 1:
        return val*-1
    elif val == 1:
        return 0

def get_totalposts(tag):
    return mydict[tag][2]

def statistics_top_hashtags(top_hashtags):
    statistics = {}
    for hshtg in top_hashtags:
        statistics[hshtg] = {"avg_likes": get_avglikes(hshtg), "like_score": get_likescore(hshtg), total_posts: get_totalposts(hshtg)}
    return statistics

def json_list():
    path_to_json_dir = os.path.dirname(os.path.abspath(_file_))+'/../../static/json'
    for _, _, filenames in os.walk(path_to_json_dir):
        return filenames

def top_cosine_sim(post_dic, input_vec, td_mat):
    top_posts = []
    cosine_sims = []
    scores = []

    for row in td_mat:
        num = np.dot(input_vec, row)
        denom = (LA.norm(input_vec))*(LA.norm(row))
        try:
            cosine_sims.append(float(num) / float(denom))
        except:
            cosine_sims.append(0)

    sorted_indicies = np.argsort(cosine_sims)[::-1]

    for i in range(0, 5):
        if(sorted_indicies[i] in post_dic):
            top_posts.append(post_dic[sorted_indicies[i]])
            scores.append(cosine_sims[sorted_indicies[i]])

    return top_posts,scores

def top_n_tags(n, top_posts):
    tags = []
    #sorted_posts = reversed(sorted(top_posts, key = lambda x : x['numberLikes']))
    for post in top_posts:
        for tag in post['tags']:
            tags.append(tag)
    return tags[:n]

def cleanup(keywords):
    keywords = keywords.split()
    processed = []
    lst = []
    for word in keywords:
        for char in word:
            if char.isalpha():
                lst.append(char.lower())
        s = "".join(lst)
        lst = []
        processed.append(s)
    return processed

def top_n_tags(top_posts, int_to_word_dict, n=10):
    words = []
    for word in top_posts:
        words.append(int_to_word_dict)

    return words[:10]

def input_vec(word_to_int_dict, keywords):
    vec = np.zeros(len(word_to_int_dict))
    for w in keywords:
        if w in word_to_int_dict:
            vec[word_to_int_dict[w]] = 1
    return vec

def input_to_tags(input_text, word_to_int_dict, post_dict, int_to_word_dict, td_mat, k=10):
    print("MIGHT BE WORKING")
    cosine_sims=[]
    top_posts=[]
    count=0
    keywords = cleanup(input_text)
    # docs_compressed, x, words_compressed = svds(td_mat.astype(float), k=10)
    print("MIGHT BE WORKING")
    words_compressed = np.load(os.getcwd()+'/words_compressed.npy') #+'/app/irsystem/models/words_compressed.npy')
    words_compressed = np.transpose(words_compressed)
    words_compressed = normalize(words_compressed, axis = 1)
    avg_input_vec = np.zeros(words_compressed.shape[1])
    print ("words compressed shape:", words_compressed.shape)

    for word in keywords:
        if word in word_to_int_dict:
            count = count + 1
            avg_input_vec = avg_input_vec + words_compressed[word_to_int_dict[word]]
    
    try:
        avg_input_vec = avg_input_vec / count
    except:
        avg_input_vec = 0

    for row in words_compressed:
        cosine_sims.append(np.dot(avg_input_vec, row))
    cosine_sims_sort = np.argsort(cosine_sims)[::-1]
    top_words = [int_to_word_dict[i] for i in cosine_sims_sort]
    top_scores = [cosine_sims[i] for i in cosine_sims_sort]
    print("top words" ,top_words[:10])
    #vec = input_vec(word_to_int_dict, top_words[:10])
    vec = np.zeros(len(word_to_int_dict))
    for i in cosine_sims_sort[:10]:
        if int_to_word_dict[i] in word_to_int_dict:
            vec[i] = cosine_sims[i]
    #print ("vec is length", len(vec))
    print ("new input vec total score", np.sum(vec))
    post_scores = []
    post_scores = np.dot(td_mat, vec)
    
    # norms = LA.norms(post_scores,axis=1)
    
    # for i in range(0, td_mat.shape[0]):
    #     sim = np.dot(td_mat[i], vec)
    #     # print ("sim:", sim)
    #     # print ("LA.norm(vec):", LA.norm(vec))
    #     # print ("LA.norm(td_mat[i])",LA.norm(td_mat[i]))
    #     # print ("i:", i)
    #     sim = sim/ ((LA.norm(vec)) * (LA.norm(td_mat[i])))
    #     post_scores.append(sim)

    print (np.sort(post_scores)[::-1][:10])
    post_arg_scores = np.argsort(post_scores)[::-1]
    top_tags = [(post_dict[j], post_scores[j]) for j in post_arg_scores]
    final_lst = []
    for tup in top_tags:
        for tag in tup[0]:
            final_lst.append((tag, tup[1]))

    return final_lst[:10]

# if _name_ == "_main_":
#     print("reading word to int")
#     word_to_int = {}
#     with open("word_to_int.csv", 'rb') as f:
#         mycsv = csv.reader(f, delimiter = ",")
#         for x, row in enumerate(mycsv):
#             if x!=0:
#                 word_to_int[row[0]] = int(row[1])
#     print("reading post to tags")
#     post_dict = {}
#     with open("/post_dict.csv", 'rb') as f:
#         mycsv = csv.reader(f, delimiter = ",")
#         for x, row in enumerate(mycsv):
#             if x!=0:
#                 mydict[row[0]] = (row[1])
#     print(input_to_tags("merry christmas", word_to_int_dict, post_dict, int_to_word_dict, k=10))


def serve_jsons():

    path_to_json_dir = os.getcwd()+'/../../static/json/'
    print ("path:", os.getcwd())
    print (path_to_json_dir)
    for _, _, filenames in os.walk(path_to_json_dir):
        json_files = [ f for f in filenames if f.endswith("json") ]
    return json_files


if __name__ == "__main__":
    #print(serve_jsons())
    word_to_int_dict, tag_to_int_dict, int_to_word_dict, int_to_tag_dict, \
    word_TDF, tag_TDF, word_inv_idx, tag_inv_idx, post_dict, word_TF_IDF, doc_norms, idf_dict = process_list_of_jsons(serve_jsons())

    print ("finished preprocessing")

    # int_to_word_dict = {}
    # word_to_int_dict = {}
    #
    # with open(os.getcwd()+"/app/irsystem/models/word_to_int.csv", 'rb') as f:
    #     mycsv = csv.reader(f, delimiter = ",")
    #     for x, row in enumerate(mycsv):
    #         if x!=0:
    #             word_to_int_dict[row[0]] = int(row[1])
    #             int_to_word_dict[int(row[1])] = row[0]
    #
    # post_dict = {}
    # with open(os.getcwd()+"/app/irsystem/models/post_dict.csv", 'rb') as f:
    #     mycsv = csv.reader(f, delimiter = ",")
    #     for x, row in enumerate(mycsv):
    #         if x!=0:
    #             post_dict[row[0]] = (row[1])
    #
    k = input_to_tags("working exercise", word_to_int_dict, post_dict, int_to_word_dict, word_TF_IDF, k=10)
    print (k)

#    word_to_int_dict, tag_to_int_dict, int_to_word_dict, int_to_tag_dict, \
#    word_TDF, tag_TDF, word_inv_idx, tag_inv_idx, post_dict, word_TF_IDF, doc_norms, idf_dict = process_list_of_jsons(['atighteru.json', 'balous_friends.json'])

#    print(input_to_tags("merry christmas", word_TDF, word_to_int_dict, post_dict, int_to_word_dict, k=10))

# from parsers_and_TFidf_setup import *
# from numpy import linalg as LA
# from scipy.sparse.linalg import svds
# from sklearn.preprocessing import normalize
# import csv
# import os
# import numpy as np

# good_tags={}
# # dict has keys = goodtag and values equal to list where the elements are avglikes, likescore, and totalposts

# with open("goodwords.csv") as f:
#     mycsv = csv.reader(f, delimiter = ",")
#     for x, row in enumerate(mycsv):
#         if x!=0:
#             good_tags[row[0]] = [float(row[1]), float(row[2]), float(row[3])]

# def get_avglikes(tag):
#     return mydict[tag][0]

# def get_likescore(tag):
#     val = float(mydict[tag][1])
#     if val > 1:
#         return float(val-1)*1.0
#     elif val < 1:
#         return val*-1
#     elif val == 1:
#         return 0

# def get_totalposts(tag):
#     return mydict[tag][2]

# def json_list():
#     path_to_json_dir = os.path.dirname(os.path.abspath(__file__))+'/../../static/json'
#     for _, _, filenames in os.walk(path_to_json_dir):
#         return filenames

# def top_cosine_sim(post_dic, input_vec, td_mat):
#     top_posts = []
#     cosine_sims = []
#     scores = []

#     for row in td_mat:
#         num = np.dot(input_vec, row)
#         denom = (LA.norm(input_vec))*(LA.norm(row))
#         try:
#             cosine_sims.append(float(num) / float(denom))
#         except:
#             cosine_sims.append(0)

#     sorted_indicies = np.argsort(cosine_sims)[::-1]

#     for i in range(0, 5):
#         if(sorted_indicies[i] in post_dic):
#             top_posts.append(post_dic[sorted_indicies[i]])
#             scores.append(cosine_sims[sorted_indicies[i]])

#     return top_posts,scores

# def top_n_tags(n, top_posts):
#     tags = []
#     #sorted_posts = reversed(sorted(top_posts, key = lambda x : x['numberLikes']))
#     for post in top_posts:
#         for tag in post['tags']:
#             tags.append(tag)
#     return tags[:n]

# def cleanup(keywords):
#     keywords = keywords.split()
#     processed = []
#     lst = []
#     for word in keywords:
#         for char in word:
#             if char.isalpha():
#                 lst.append(char.lower())
#         s = "".join(lst)
#         lst = []
#         processed.append(s)
#     return processed

# def top_n_tags(top_posts, int_to_word_dict, n=10):
#     words = []
#     for word in top_posts:
#         words.append(int_to_word_dict)

#     return words[:10]

# def input_vec(word_to_int_dict, keywords):
#     vec = np.zeros(len(word_to_int_dict))
#     for w in keywords:
#         if w in word_to_int_dict:
#             vec[word_to_int_dict[w]] = 1
#     return vec

# def input_to_tags(input_text, td_mat, word_to_int_dict, post_dict, int_to_word_dict, k=10):
#     cosine_sims=[]
#     top_posts=[]
#     count=0
#     keywords = cleanup(input_text)
#     words_compressed = np.load(os.getcwd()+'/app/irsystem/models/words_compressed.npy')
#     words_compressed = np.transpose(words_compressed)
#     words_compressed = normalize(words_compressed, axis = 1)
#     avg_input_vec = np.zeros(words_compressed.shape[1])

#     for word in keywords:
#         if word in word_to_int_dict:
#             count = count + 1
#             avg_input_vec = avg_input_vec + words_compressed[word_to_int_dict[word]]
#     try:
#         avg_input_vec = avg_input_vec / count
#     except:
#         avg_input_vec = 0

#     for row in words_compressed:
#         cosine_sims.append(np.dot(avg_input_vec, row))

#     cosine_sims = np.argsort(cosine_sims)[::-1]
#     top_words = [int_to_word_dict[i] for i in cosine_sims]
#     vec = input_vec(word_to_int_dict, top_words[:10])

#     post_scores = []
#     for i in range(0, td_mat.shape[0]):
#         sim = np.dot(td_mat[i], vec)
#         sim = sim / ((LA.norm(vec)) * (LA.norm(td_mat[i])))
#         post_scores.append(sim)
#     post_arg_scores = np.argsort(post_scores)[::-1]
#     top_tags = [(post_dict[j], post_scores[j]) for j in post_arg_scores]
#     final_lst = []
#     for tup in top_tags:
#         for tag in tup[0]:
#             final_lst.append((tag, tup[1]))

#     return final_lst[:10]

# if __name__ == "__main__":
#     print("reading word to int")
#     word_to_int = {}
#     with open("word_to_int.csv", 'rb') as f:
#         mycsv = csv.reader(f, delimiter = ",")
#         for x, row in enumerate(mycsv):
#             if x!=0:
#                 mydict[row[0]] = int(row[1])
#     print("reading post to tags")
#     post_dict = {}
#     with open("/post_dict.csv", 'rb') as f:
#         mycsv = csv.reader(f, delimiter = ",")
#         for x, row in enumerate(mycsv):
#             if x!=0:
#                 mydict[row[0]] = (row[1])
#     print(input_to_tags("merry christmas", word_to_int_dict, post_dict, int_to_word_dict, k=10))


# #    word_to_int_dict, tag_to_int_dict, int_to_word_dict, int_to_tag_dict, \
# #    word_TDF, tag_TDF, word_inv_idx, tag_inv_idx, post_dict, word_TF_IDF, doc_norms, idf_dict = process_list_of_jsons(['atighteru.json', 'balous_friends.json'])

# #    print(input_to_tags("merry christmas", word_TDF, word_to_int_dict, post_dict, int_to_word_dict, k=10))
