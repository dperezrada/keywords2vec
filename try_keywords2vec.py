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
        "-v", "--vector_path", dest="vector_path",
        required=True, help="the path to the vector model. This is an alternative of using the directory + name",
        metavar="VECTOR_MODEL_PATH"
    )
    parser.add_argument(
        "-c", "--counter_path", dest="counter_path",
        required=False, help="counter path",
        metavar="COUNTER_PATH", default=""
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

    keywords_vectors = load_vectors(args.vector_path)

    counter = None
    if args.counter_path:
        counter = load_counter(args.counter_path)
    positive_keywords = [key for key in args.positive.split(",") if key]
    negative_keywords = [key for key in args.negative.split(",") if key]
    try_model(
        keywords_vectors, positive_keywords, negative_keywords, total_results=args.top_similars, counter=counter
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
        try:
            keyword, total = line[0:-1].split("\t")
            if keyword:
                counter_dict[keyword] = int(total)
        except:
            pass
    counter = Counter(counter_dict)
    del counter_dict
    return counter

def try_model(
        keywords_vectors,
        positive_keywords, negative_keywords, total_results=25, counter=None
    ):
    if not counter:
        counter = {}
    most_similars = [
        (keyword, score, counter.get(keyword, '?'))
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
