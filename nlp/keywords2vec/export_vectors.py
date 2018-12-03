import os
import gzip
from argparse import ArgumentParser
from collections import Counter

import gensim

def main():
    parser = ArgumentParser()
    parser.add_argument(
        "-v", "--vector_path", dest="vector_path",
        required=True, help="the path to the .vec model",
        metavar="VECTOR_MODEL_PATH"
    )
    parser.add_argument(
        "-o", "--output-directory", dest="output",
        required=False, help="the output directory for the outputs",
        metavar="DIRECTORY", default="data/exports/experiment_1"
    )
    parser.add_argument(
        "-s", "--size", dest="size",
        required=False, help="the number of vectors you wanted to export. Default to all",
        metavar="SIZE", default="all"
    )
    parser.add_argument(
        "-p", "--prefix", dest="prefix",
        required=False, help="prefix to pre-append to the file name",
        metavar="PREFIX", default=""
    )

    args = parser.parse_args()

    keywords_vectors = load_vectors(args.vector_path)

    export_vector(keywords_vectors, args.output, args.size, args.prefix)

## Load the vectors
def load_vectors(store_model_path):
    keywords_vectors = gensim.models.KeyedVectors.load(
        store_model_path, mmap='r'
    )
    return keywords_vectors

def export_vector(keywords_vectors, output_dir, max_number, prefix=""):
    if prefix:
        prefix = "%s_" % prefix
    words_path = os.path.join(output_dir, "%swords.tsv" % prefix)
    vectors_path = os.path.join(output_dir, "%svectors.tsv" % prefix)
    max_index = 0
    if max_number != "all":
        max_index = int(max_number)
    index = 0
    with open(words_path, "wt") as file_words:
        with open(vectors_path, "wt") as file_vec:
            for keyword in keywords_vectors.vocab.keys():
                try:
                    vector_str = "\t".join(
                        (
                            [
                                str(round(vector_i, 3))
                                for vector_i in keywords_vectors[keyword]
                            ]
                        )
                    ) + "\n"
                    if vector_str.find("nan") >= 0:
                        continue
                    file_vec.write(vector_str)
                    file_words.write(keyword.replace(" ", "_") + "\n")
                except:
                    continue
                index += 1
                if max_index and index > max_index:
                    break


if __name__ == '__main__':
    main()
