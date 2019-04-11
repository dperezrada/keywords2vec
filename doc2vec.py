import os
import gzip
import math
from argparse import ArgumentParser
from collections import Counter

import numpy as np
import gensim
from numpy.linalg import norm

from keywords2vec import tokenize_text, log


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "-i", "--input-file", dest="input_filename",
        required=True, help="the input text file", metavar="INPUT_FILE"
    )
    parser.add_argument(
        "-c", "--column-numbers", dest="column_numbers",
        required=False, help="The text columns of the file. Allowed multiple, separed by comma (starting from 0)",
        metavar="column_numbers", default="0", type=str
    )
    parser.add_argument(
        "-k", "--key_column", dest="key_column",
        required=True, help="The key that identify each document.",
        metavar="COLUMN_ID", default="-1", type=int
    )
    parser.add_argument(
        "-d", "--delimiter", dest="delimiter", required=False,
        help="the column delimiter", metavar="DELIMITER", default="\t"
    )
    parser.add_argument(
        "-o", "--output-directory", dest="output_directory",
        required=False, help="the target directory for the outputs",
        metavar="DIRECTORY", default="data/experiments"
    )
    parser.add_argument(
        "-n", "--name", dest="name",
        required=False, help="name of the experiment",
        metavar="NAME", default="experiment_1"
    )
    parser.add_argument(
        "-l", "--lines-chunks", dest="lines_chunks",
        required=False, help="size of the lines chunks, to use as progress update",
        metavar="LINES_CHUNKS", default="15000", type=int
    )
    parser.add_argument(
        "-s", "--sample", dest="sample_size",
        required=False,
        help="if you wanted to process a sample of the lines. By default -1 (all)",
        metavar="SIZE", default="-1", type=int
    )
    parser.add_argument(
        "-q", "--quiet",
        dest="verbose", default=True,
        help="don't print status messages to stdout"
    )
    parser.add_argument(
        "-a", "--additional-stopwords", dest="additional_stopwords",
        required=False,
        help="Stopwords must be separated by comma",
        metavar="STOPWORDS", default="", type=str
    )

    args = parser.parse_args()
    args.experiment_path = os.path.join(args.output_directory, args.name)
    if not os.path.exists(args.experiment_path):
        os.makedirs(args.experiment_path)
    if args.sample_size > 0 and args.sample_size < args.lines_chunks:
        args.lines_chunks = args.sample_size

    args.tokenized_path = os.path.join(args.experiment_path, "doc2vec_tokenized.tsv.gz")

    keywords_vectors = load_vectors(args)

    step = 1
    log("Step%s: Tokenizing" % step, args.verbose)
    tokenize_text(args)
    step += 1

    log("Step%s: Generating doc2vec" % step, args.verbose)
    doc2vec_model = gensim.models.keyedvectors.Word2VecKeyedVectors(
        keywords_vectors.vector_size
    )
    index = 0
    ids = []
    vectors = []
    for line in gzip.open(args.tokenized_path, "rt"):
        try:
            id_, text = line.split("\t")
        except:
            pass
        ids.append(id_)
        vectors.append(text_to_vector(keywords_vectors, text))
        if index % args.lines_chunks == 0:
            log(
                "%s lines processed" % (index),
                verbose=args.verbose, inline=False
            )
        index += 1
    doc2vec_model.add(ids, vectors)

    # log("Step%s: Reading keywords" % step, args.verbose)
    # documents_keywords = read_documents(tokenized_path)
    # step += 1

    # log("Step%s: Calculate frequency" % step, args.verbose)
    # counter = calculate_keywords_frequency(documents_keywords)
    # step += 1

    # log("Step%s: Generate word2vec model" % step, args.verbose)
    # keywords_vectors = generate_word2vec_model(documents_keywords, args)
    # step += 1

    log("Step%s: Save vectors" % step, args.verbose)
    save_vectors(doc2vec_model, args)
    step += 1

    # log("Step%s: Save counter" % step, args.verbose)
    # save_counter(counter, args)
    # step += 1

## Load the vectors
def load_vectors(args):
    store_model_path = os.path.join(args.experiment_path, "word2vec.vec")
    keywords_vectors = gensim.models.KeyedVectors.load(
        store_model_path, mmap='r'
    )
    return keywords_vectors

def text_to_vector(keywords_vectors, text):
    to_return_vector = np.zeros(keywords_vectors.vector_size)
    change_step = 7
    mult_num = 10

    all_keywords = text.split("!")

    norm_el = 0
    current_step = 1
    for keyword_index, keyword in enumerate(all_keywords):
        mult_el = math.pow(mult_num, 1 / current_step)
        norm_el += mult_el
        if keyword in keywords_vectors:
            if not np.isnan(keywords_vectors[keyword][0]):
                to_return_vector += mult_el * keywords_vectors[keyword]
                if keyword_index % change_step == 0:
                    current_step += 2
    return (to_return_vector / norm(to_return_vector)) / norm_el

## Save the vectors
def save_vectors(keywords_vectors, args):
    store_model_path = os.path.join(args.experiment_path, "doc2vec.vec")
    keywords_vectors.save(store_model_path)
    return store_model_path

if __name__ == '__main__':
    main()
