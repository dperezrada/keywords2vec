import gzip
import json
import os
from collections import Counter, defaultdict

import gensim
from flask import Flask, request, Response, send_from_directory

app = Flask(__name__, static_url_path='')

VECTORS_PATH=os.environ["VECTORS_PATH"]
MIN_TOTAL=5

def load_vectors(vectors_path):
    if os.path.exists(vectors_path):
        return gensim.models.KeyedVectors.load(
            vectors_path, mmap='r'
        )

def load_counter(counter_path):
    counter_dict = {}
    for line in gzip.open(counter_path, "rt"):
        keyword, total = line[0:-1].split("\t")
        if keyword:
            counter_dict[keyword] = int(total)
    counter = Counter(counter_dict)
    del counter_dict
    return counter

def load_tokenized_keywords_docs(file_path):
    documents = {}
    inv_documents = {}
    keywords_docs = defaultdict(list)
    current_index = 0
    if os.path.exists(file_path):
        for line in gzip.open(file_path, "rt"):
            try:
                doc_id, text = line[0:-1].split("\t")
            except:
                continue
            if documents.get(doc_id) is None:
                documents[doc_id] = current_index
                inv_documents[current_index] = doc_id
                current_index += 1
            doc_index = documents[doc_id]
            for keyword in set(text.split("!")):
                if keyword:
                    keywords_docs[keyword].append(doc_index)
            if current_index % 25000 == 0:
                print("Loaded %s" % current_index, end="\r")
    return inv_documents, keywords_docs

VECTORS = load_vectors(os.path.join(VECTORS_PATH, "word2vec.vec"))
INV_DOCUMENTS, KEYWORDS_DOCS = load_tokenized_keywords_docs(os.path.join(VECTORS_PATH, "doc2vec_tokenized.tsv.gz"))
COUNTER = load_counter(os.path.join(VECTORS_PATH, "keywords_counter.tsv.gz"))



def get_keywords_list(target_parameter):
    return [
        keyword.strip()
        for keyword in request.args.get(target_parameter, '').split(",")
        if keyword.strip()
    ]

@app.route('/')
def home():
    return send_from_directory('.', "index.html")

@app.route('/public/<path:path>')
def public_files(path):
    return send_from_directory('public', path)

@app.route("/keywords/similars")
def get_similar_keywords():
    positive_keywords = get_keywords_list("positive")
    negative_keywords = get_keywords_list("negative")
    n_results = 25
    max_results = 250
    try:
        n_results = min(int(request.args.get("size")) or n_results, max_results)
    except:
        pass
    most_similars = [
        (keyword, round(score, 5), COUNTER.get(keyword, 0))
        for keyword, score in VECTORS.most_similar(
            positive=positive_keywords,
            negative=negative_keywords,
            topn=n_results
        )
    ]
    return Response(json.dumps(most_similars), mimetype='application/json')

@app.route("/keywords/match_docs")
def match_docs():
    groups = (request.args.get("keywords") or "").lower().split("::")
    groups_docs = []
    for group_text in groups:
        docs = []
        for keyword in group_text.split(","):
            docs += KEYWORDS_DOCS.get(keyword) or []
        groups_docs.append(set(docs))
    if len(groups_docs) > 1:
        intersected_docs = set.intersection(*groups_docs)
    else:
        intersected_docs = groups_docs[0]
    return Response(
        json.dumps(
            [
                INV_DOCUMENTS[doc_index]
                for doc_index in list(intersected_docs)
            ]
        ), mimetype='application/json'
    )

@app.route("/keywords/all")
def get_keywords_all():
    # for keyword, total in COUNTER.most_common():
    #     if total < MIN_TOTAL:
    #         break
    #     keywords.append(keyword)
    return Response(json.dumps(list(VECTORS.vocab.keys())), mimetype='application/json')
