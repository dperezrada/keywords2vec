import os
import gzip
from argparse import ArgumentParser
from collections import Counter

import gensim
import pandas as pd

from keywords_tokenizer import tokenize_one


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "-i", "--input-file", dest="input_filename",
        required=True, help="the input text file", metavar="INPUT_FILE"
    )
    parser.add_argument(
        "-c", "--column-numbers", dest="column_numbers",
        required=False, help="The text columns of the file. Allowed multiple, separed by comma (starting from 0)",
        metavar="COLUM_NUMBERS", default="0", type=str
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
        metavar="LINES_CHUNKS", default="5000", type=int
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
    parser.add_argument(
        "--word2vec_size", dest="word2vec_size",
        required=False,
        help="Word2vec vector size",
        metavar="WORD2VEC_SIZE", default="300", type=int
    )
    parser.add_argument(
        "--word2vec_window", dest="word2vec_window",
        required=False,
        help="Word2vec window size",
        metavar="WORD2VEC_WINDOW", default="5", type=int
    )
    parser.add_argument(
        "--word2vec_count", dest="word2vec_count",
        required=False,
        help="Word2vec min keyword count",
        metavar="WORD2VEC_MIN_COUNT", default="3", type=int
    )
    parser.add_argument(
        "--word2vec_epochs", dest="word2vec_epochs",
        required=False,
        help="Word2vec epochs number",
        metavar="WORD2VEC_EPOCHS", default="20", type=int
    )
    parser.add_argument(
        "--workers", dest="workers",
        required=False,
        help="Total numbers of CPU workers",
        metavar="CPU_WORKERS", default="4", type=int
    )
    args = parser.parse_args()
    args.experiment_path = os.path.join(args.output_directory, args.name)
    if not os.path.exists(args.experiment_path):
        os.makedirs(args.experiment_path)
    if args.sample_size > 0 and args.sample_size < args.lines_chunks:
        args.lines_chunks = args.sample_size

    step = 1
    log("Step%s: Tokenizing" % step, args.verbose)
    tokenized_path = os.path.join(args.experiment_path, "tokenized.txt.gz")
    if not os.path.exists(tokenized_path):
        tokenized_path = tokenize_text(args)
    else:
        log("File already exists", args.verbose)
    step += 1


    log("Step%s: Reading keywords" % step, args.verbose)
    documents_keywords = read_documents(tokenized_path)
    step += 1

    log("Step%s: Calculate frequency" % step, args.verbose)
    counter, _ = calculate_keywords_frequency(documents_keywords)
    step += 1

    log("Step%s: Generate word2vec model" % step, args.verbose)
    keywords_vectors = generate_word2vec_model(documents_keywords, args)
    step += 1

    log("Step%s: Save vectors" % step, args.verbose)
    save_vectors(keywords_vectors, args)
    step += 1

    log("Step%s: Save counter" % step, args.verbose)
    save_counter(counter, args)
    step += 1

def tokenize_text(args):
    """This is the parts where we are goint to separate the text, according to the following rules.
    We are goint to use the stopwords to separate the different expression,
    and in that way identify keywords, as an alternative to use ngrams.
    Example (! is used as separator of the keywords):
        - input: "Timing of replacement therapy for acute renal failure after cardiac surgery"
        - output: "timing!replacement therapy!acute renal failure!cardiac surgery"
    Another example:
        - input: "Acute renal failure (ARF) following cardiac surgery remains a significant cause of mortality. The aim of this study is to compare early and intensive use of continuous veno-venous hemodiafiltration (CVVHDF) with conservative usage of CVVHDF in patients with ARF after cardiac surgery."
        - output: "acute renal failure!arf!following cardiac surgery remains!significant cause!mortality!aim!study!compare early!intensive!continuous veno-venous hemodiafiltration!cvvhdf!conservative usage!cvvhdf!patients!arf!cardiac surgery"
    """
    tokenized_path = os.path.join(args.experiment_path, "tokenized.txt.gz")


    index = 0
    with gzip.open(tokenized_path, "wt") as _output:
        # We are going to split the text in chunks to show some progress.
        for text_part in get_file_chunks(args.input_filename, args.lines_chunks, args):
            text_part = tokenize_one(
                text_part,
                additional_stopwords=args.additional_stopwords.split(",")
            )
            _output.write(text_part)
            index += 1
            log(
                "%s lines processed" % (index * args.lines_chunks),
                verbose=args.verbose, inline=True
            )
            if args.sample_size > 0 and index * args.lines_chunks >= args.sample_size:
                break
    return tokenized_path

def get_file_chunks(filepath, lines_chunk, args):
    with gzip.open(filepath, "rt") as _file:
        while True:
            next_n_lines = list(chunk_of_text(_file, lines_chunk, args))
            yield "\n".join(next_n_lines)
            if not next_n_lines:
                break

def chunk_of_text(_file, chunk_size, args):
    index = 0
    while True:
        line = _file.readline()
        if not line:
            break
        tmp_text_parts = line.lower()[:-1].split(args.delimiter)
        selected_text_parts = ". ".join([
            tmp_text_parts[int(col_numb)] + ". "
            for col_numb in args.column_numbers.split(",")
        ])
        del tmp_text_parts

        for sentence in selected_text_parts.split("."):
            if sentence.strip():
                yield sentence.strip()
        if index >= chunk_size:
            break
        index += 1

def log(line, verbose=True, inline=False):
    end = "\n"
    if verbose:
        if inline:
            end = "\r"
        print(line, end=end)

### Read tokenized data
def read_documents(tokenized_path):
    documents_keywords = []
    index = 0
    for line in gzip.open(tokenized_path, "rt"):
        documents_keywords.append(line[0:-1].split("!"))
        index += 1
    return documents_keywords

# ## Calculate words frequency

def calculate_keywords_frequency(documents_keywords):
    counter = Counter([
        keyword
        for keywords in documents_keywords
        for keyword in keywords
    ])
    counter_frame = pd.DataFrame.from_dict(counter, orient='index').reset_index()
    counter_frame = counter_frame.rename(columns={'index':'term', 0:'count'})
    return counter, counter_frame

def generate_word2vec_model(documents_keywords, args):
    total_documents = len(documents_keywords)
    model = gensim.models.Word2Vec(
        documents_keywords, size=args.word2vec_size, window=args.word2vec_window,
        min_count=args.word2vec_count, workers=args.workers
    )
    model.train(
        documents_keywords, total_examples=total_documents,
        epochs=args.word2vec_epochs
    )
    return model.wv

## Save the vectors
def save_vectors(keywords_vectors, args):
    store_model_path = os.path.join(args.experiment_path, "word2vec.vec")
    keywords_vectors.save(store_model_path)
    return store_model_path


def save_counter(counter, args):
    counter_store_path = os.path.join(args.experiment_path, "keywords_counter.tsv.gz")
    with gzip.open(counter_store_path, 'wt') as _file:
        for term, total in counter.most_common():
            _file.write("%s\t%s\n" % (term, total))
    return counter_store_path

if __name__ == '__main__':
    main()
