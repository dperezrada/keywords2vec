import os
import gzip
from argparse import ArgumentParser
from collections import Counter
import pandas as pd

import gensim

def main():
    parser = ArgumentParser()
    parser.add_argument(
        "-d", "--directory", dest="directory",
        required=False, help="the target directory for the outputs",
        metavar="DIRECTORY", default="data/experiments"
    )
    parser.add_argument(
        "-n", "--name", dest="name",
        required=False, help="name of the experiment",
        metavar="NAME", default="experiment_1"
    )
    parser.add_argument(
        "-p", "--positive", dest="positive",
        required=True, help="positive keywords",
        metavar="POSITIVE"
    )
    parser.add_argument(
        "--negative", dest="negative",
        required=False, help="negative keywords",
        metavar="NEGATIVE", default=""
    )
    parser.add_argument(
        "-t", dest="top_similars",
        required=False, help="Number of similar keywords",
        metavar="TOP_SIMILARS", default="25", type=int
    )
    args = parser.parse_args()
    args.experiment_path = os.path.join(args.directory, args.name)

    store_model_path = os.path.join(args.experiment_path, "word2vec.vec")
    keywords_vectors = load_vectors(store_model_path)

    counter_store_path = os.path.join(args.experiment_path, "keywords_counter.tsv.gz")
    counter = load_counter(counter_store_path)
    positive_keywords = [key for key in args.positive.split(",") if key]
    negative_keywords = [key for key in args.negative.split(",") if key]
    try_model(
        keywords_vectors, counter, positive_keywords, negative_keywords, total_results=args.top_similars
    )


## Load the vectors
def load_vectors(store_model_path):
    keywords_vectors = gensim.models.KeyedVectors.load(
        store_model_path, mmap='r'
    )
    return keywords_vectors

def load_counter(counter_path):
    counter_dict = {}
    for line in gzip.open(counter_path, "rt"):
        keyword, total = line[0:-1].split("\t")
        if keyword:
            counter_dict[keyword] = int(total)
    counter = Counter(counter_dict)
    del counter_dict
    return counter

def try_model(
        keywords_vectors, counter,
        positive_keywords, negative_keywords, total_results=25
    ):
    most_similars = [
        (keyword, score, counter.get(keyword, 0))
        for keyword, score in keywords_vectors.most_similar(
            positive=positive_keywords,
            negative=negative_keywords, topn=int(total_results)
        )
    ]
    print(
        pd.DataFrame(
            most_similars,
            columns=["term", "score", "counter"]
        ).to_string()
    )

if __name__ == '__main__':
    main()
