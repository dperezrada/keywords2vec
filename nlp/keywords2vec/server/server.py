import gzip
import json
import os
from collections import Counter

import gensim
from flask import Flask, request, Response, send_from_directory
app = Flask(__name__, static_url_path='')

VECTORS_PATH=os.environ["VECTORS_PATH"]

def load_vectors(vectors_path):
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

VECTORS = load_vectors(os.path.join(VECTORS_PATH, "word2vec.vec"))
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

@app.route("/keywords")
def get_keywords():
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
