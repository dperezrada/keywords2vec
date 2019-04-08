import re
from nltk import RegexpParser
import nltk
import unidecode
import scispacy
import spacy


NLP = spacy.load("en_core_sci_sm")
STOPWORDS = {
    "en": [
        "several", "on", "while", "than", "own", "you've", "itself", "above", "such", "over", "they're", "mainly", "because", "theirs", "too", "most", "must", "myself", "that", "why's", "it", "can't", "show", "overall", "she", "he'd", "it's", "can", "under", "no", "she'll", "should", "therefore", "his", "you", "various", "mustn't", "are", "doing", "really", "up", "they'd", "having", "these", "made", "we'll", "into", "you'll", "more", "ought", "especially", "hasn't", "seem", "nor", "shows", "here's", "here", "he's", "is", "at", "ml", "always", "nearly", "during", "ours", "this", "aren't", "rather", "being", "very", "shown", "them", "cannot", "just", "or", "where", "didn't", "another", "they'll", "shouldn't", "wasn't", "for", "when's", "in", "could", "off", "down", "further", "won't", "due", "however", "each", "i'd", "a", "that's", "where's", "enough", "neither", "its", "isn't", "any", "himself", "was", "they've", "etc", "there's", "whom", "both", "other", "by", "within", "not", "been", "below", "be", "once", "make", "does", "did", "before", "through", "shan't", "ourselves", "which", "kg", "their", "again", "thus", "about", "few", "either", "they", "do", "our", "you'd", "some", "don't", "although", "almost", "i'll", "often", "i'm", "she'd", "we'd", "yourselves", "using", "between", "if", "upon", "him", "we", "done", "as", "so", "hers", "me", "she's", "there", "and", "i've", "may", "but", "with", "how", "found", "her", "yours", "might", "then", "we've", "the", "yourself", "what's", "km", "without", "same", "those", "my", "perhaps", "all", "haven't", "of", "why", "has", "had", "regarding", "significantly", "when", "i", "until", "used", "would", "among", "what", "let's", "am", "how's", "who's", "weren't", "mm", "hadn't", "have", "mg", "wouldn't", "showed", "were", "an", "we're", "obtained", "themselves", "who", "your", "out", "to", "doesn't", "he", "herself", "pmid", "against", "use", "you're", "couldn't", "after", "he'll", "only", "also", "mostly", "quite", "seen", "since"
    ]
}

NUMBERS_STOPWORDS = {
    "en": [
        "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "twenty-one", "twenty-two", "twenty-three", "twenty-four", "twenty-five", "twenty-six", "twenty-seven", "twenty-eight", "twenty-nine", "thirty", "thirty-one", "thirty-two", "thirty-three", "thirty-four", "thirty-five", "thirty-six", "thirty-seven", "thirty-eight", "thirty-nine", "forty", "forty-one", "forty-two", "forty-three", "forty-four", "forty-five", "forty-six", "forty-seven", "forty-eight", "forty-nine", "fifty", "fifty-one", "fifty-two", "fifty-three", "fifty-four", "fifty-five", "fifty-six", "fifty-seven", "fifty-eight", "fifty-nine", "sixty", "sixty-one", "sixty-two", "sixty-three", "sixty-four", "sixty-five", "sixty-six", "sixty-seven", "sixty-eight", "sixty-nine", "seventy", "seventy-one", "seventy-two", "seventy-three", "seventy-four", "seventy-five", "seventy-six", "seventy-seven", "seventy-eight", "seventy-nine", "eighty", "eighty-one", "eighty-two", "eighty-three", "eighty-four", "eighty-five", "eighty-six", "eighty-seven", "eighty-eight", "eighty-nine", "ninety", "ninety-one", "ninety-two", "ninety-three", "ninety-four", "ninety-five", "ninety-six", "ninety-seven", "ninety-eight", "ninety-nine"
    ]
}
# Tokenize


def prepare_stopwords(stopwords=None, additional_stopwords=None, lang="en"):
    if stopwords is None:
        stopwords = STOPWORDS[lang] + NUMBERS_STOPWORDS[lang]
    if additional_stopwords:
        stopwords += additional_stopwords
    return [
        stopword
        for stopword in stopwords
        if stopword
    ]


def tokenize_one(text, stopwords=None, additional_stopwords=None, lang="en"):
    stopwords = prepare_stopwords(stopwords, additional_stopwords, lang)
    text_part = text.lower()

    # Must be executed in order
    regexs = [
        # Remove all stopwords by a !, we are searching for the stopword (bounded)
        ("\\b" + "\\b|\\b".join(stopwords), "!!"),
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
    ]
    for regex, replacement in regexs:
        text_part = re.sub(regex, replacement, text_part, flags=re.M)
    return text_part


# Second option to tokenize the information
def get_nodes_for_ntlk(parent, stopwords):
    keywords = []
    for node in parent:
        if type(node) is nltk.Tree:
            phrase = " ".join([key.lower() for key, value in node.leaves()])
            phrase = unidecode.unidecode(phrase)
            if phrase not in stopwords:
                pattern = re.compile('([^\s\w-]|_)+')
                phrase = pattern.sub('', phrase).strip()
                keywords.append(phrase)
    return keywords


def tokenize_by_nltk(text, stopwords=None, additional_stopwords=None, lang="en"):
    stopwords = prepare_stopwords(stopwords, additional_stopwords, lang)
    grammar = r'KT: {(<JJ>* <NN.*>+ <IN>)? <JJ>* <NN.*>+}'
    chunker = RegexpParser(grammar)

    sentences = nltk.sent_tokenize(text)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    keyphrases = []
    relevant_words = set()
    for s in sentences:
        keyphrases.append(chunker.parse(s))
    for elem in keyphrases:
        relevant_words.update(get_nodes_for_ntlk(elem, stopwords))
    return "!".join(relevant_words)


def clean_keywords(keywords):
    return [
        str(keyword).lower().strip()
        for keyword in keywords
    ]


def scispacy_tokenizer(text, stopwords=None, additional_stopwords=None, lang="en"):
    doc = NLP(text)
    return "!".join(clean_keywords(doc.ents))
