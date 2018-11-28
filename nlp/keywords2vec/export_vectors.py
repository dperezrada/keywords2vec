import os
import gzip
from argparse import ArgumentParser
from collections import Counter

import gensim

def main():
    parser = ArgumentParser()
    parser.add_argument(
        "-d", "--directory", dest="experiment_path",
        required=False, help="the directory where the word2vec and keywords_counter is located",
        metavar="DIRECTORY", default="data/experiments/experiment_1"
    )
    parser.add_argument(
        "-o", "--output-directory", dest="output",
        required=False, help="the output directory for the outputs",
        metavar="DIRECTORY", default="data/exports/experiment_1"
    )

    args = parser.parse_args()

    store_model_path = os.path.join(args.experiment_path, "word2vec.vec")
    keywords_vectors = load_vectors(store_model_path)

    counter_store_path = os.path.join(args.experiment_path, "keywords_counter.tsv.gz")
    counter = load_counter(counter_store_path)
    export_vector(keywords_vectors, counter)

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

def export_vector(keywords_vectors, counter, output_dir):
    words_path = os.path.join(output_dir, "words.tsv.gz")
    vectors_path = os.path.join(output_dir, "vectors.tsv.gz")
    with gzip.open(words_path, "wt") as file_words:
        with gzip.open(vectors_path, "wt") as file_vec:
            for keyword, _ in counter.most_common():
                try:
                    file_vec.write(
                        "\t".join(
                            (
                                #[keyword,] +
                                [
                                    str(round(vector_i, 5))
                                    for vector_i in keywords_vectors[keyword]
                                ]
                            )
                        ) + "\n"
                    )
                    file_words.write(keyword.replace(" ", "_") + "\n")
                except:
                    continue


if __name__ == '__main__':
    main()
