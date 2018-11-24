import os
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
        metavar="NEGATIVE", default="50", type=int
    )
    args = parser.parse_args()
    args.experiment_path = os.path.join(args.directory, args.name)

    store_model_path = os.path.join(args.experiment_path, "word2vec.vec")
    keywords_vectors = load_vectors(store_model_path)

    counter_store_path = os.path.join(args.experiment_path, "keywords_counter.tsv")
    _, counter_frame = load_counter(counter_store_path)
    try_model(
        keywords_vectors, counter_frame,
        args.positive.split(","), args.negative.split(","), total_results=args.top_similars
    )


## Load the vectors
def load_vectors(store_model_path):
    keywords_vectors = gensim.models.KeyedVectors.load(
        store_model_path, mmap='r'
    )
    return keywords_vectors

def load_counter(counter_path):
    counter_dict = {}
    for line in open(counter_path):
        keyword, total = line[0:-1].split("\t")
        counter_dict[keyword] = total
    counter = Counter(counter_dict)
    del counter_dict
    counter_frame = pd.DataFrame.from_dict(counter, orient='index').reset_index()
    counter_frame = counter_frame.rename(columns={'index':'term', 0:'count'})
    return counter, counter_frame

def try_model(
        keywords_vectors, counter_frame,
        positive_keywords, negative_keywords, total_results=25
    ):
    top_similars = pd.DataFrame(
        keywords_vectors.most_similar(
            positive=positive_keywords,
            negative=negative_keywords, topn=total_results
        ),
        columns=["term", "score"]
    )
    if counter_frame:
        keywords_similar = top_similars.merge(
            counter_frame, on='term', how='left'
        )
        print(keywords_similar.to_string())
    else:
        print(top_similars.to_string())

if __name__ == '__main__':
    main()
