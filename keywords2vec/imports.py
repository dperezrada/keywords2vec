import gzip
import os
import re

import unidecode
import nltk

from stop_words import safe_get_stop_words
from annoy import AnnoyIndex
