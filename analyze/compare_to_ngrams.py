import re
import gzip
import sys

from multiprocessing import Pool, cpu_count
from functools import partial


from keywords_tokenizer import tokenize_one

def tokenize_simple(text):
    text_part = text.lower()

    # Must be executed in order
    regexs = [
        ("’", "'"),
        # Remove all non alpha, numeric, spaces, - or single quote
        (r'([^a-z0-9\u00C0-\u1FFF\u2C00-\uD7FF \t\n\-\'])', "!!"),
        # remove only words numbers
        (r'(^|[ !])[0-9]+([ !]|$)', "!!"),
        # remove hyphen-minus for keywords starting or ending with it
        (r'((^|[ !])[\-\']+)|([\-\']+([ !]|$))', "!!"),
        # remove spaces between !
        (r' *! *', "!!"),
        # generate multiple ! need for next regex
        (r'!', "!!"),
        # remove one character keyword
        (r'(^|!)[^!\n](!|$)', "!!"),
        # remove multiple ! (!!!!)
        (r'!+', "!"),
        # remove first and last !
        (r'(^!+)|(!+$)', ""),
        # replace spaces
        (r'\s', "!"),
    ]
    for regex, replacement in regexs:
        text_part = re.sub(regex, replacement, text_part, flags=re.M)
    return text_part.split("!")


def get_ngram(text, min_ngram=1, max_ngrams=6):
    list_of_words = tokenize_simple(text)
    ngrams = {}
    for ngram in range(min_ngram, max_ngrams):
        ngrams[ngram] = [
            " ".join(list_of_words[i:i + ngram])
            for i in iter(range(len(list_of_words) - ngram + 1))
        ]
    return ngrams

def process_batch_grams(texts):
    cpu_num = max(1, cpu_count() - 1)
    pool_queue = Pool(cpu_num)

    ngrams_rows = pool_queue.map(get_ngram, texts)
    pool_queue.close()
    for ngrams_found in ngrams_rows:
        for ngram_num, keywords in ngrams_found.items():
            for keyword in keywords:
                print("%s\t%s" % (ngram_num, keyword))

# Could be refactored later
def process_batch_stopwords_tokenizer(texts):
    cpu_num = max(1, cpu_count() - 1)
    pool_queue = Pool(cpu_num)

    rows = pool_queue.map(tokenize_one, texts)
    pool_queue.close()
    for ngrams_found in rows:
        for ngram_num, keywords in ngrams_found.items():
            for keyword in keywords:
                print("%s\t%s" % ("sk", keyword))

def main():
    ngrams = (1, 6)
    batch_size = 10000
    cpu_num = max(1, cpu_count() - 1)
    pool_queue = Pool(cpu_num)

    texts = []
    for index, line in enumerate(gzip.open(sys.argv[1], "rt")):
        row = line[:-1].split("\t")
        title = row[2]
        abstract = row[3]
        text = title + "." + abstract
        if index > 0 and index % batch_size == 0:
            process_batch_grams(texts)
            process_batch_stopwords_tokenizer(texts)
            texts = []
            print(index, end="\r", file=sys.stderr)
    if len(texts) > 0:
        process_batch_grams(texts)
        process_batch_stopwords_tokenizer(texts)

if __name__ == '__main__':
    main()
