# Keywords2vec

## Main idea

To generate a word2vec model, but using multi-word keywords instead of single words.

## Example

Finding similar keywords for "__obesity__"

| index | term                        | score          | count |
|-------|-----------------------------|----------------|-------|
| 0     | overweight                  | 0.500965       | 297   |
| 1     | obese individuals           | 0.479940       | 15    |
| 2     | obese                       | 0.470804       | 152   |
| 3     | hypertension                | 0.444629       | 838   |
| 4     | obese adults                | 0.444151       | 28    |
| 5     | bariatric surgery           | 0.441297       | 83    |
| 6     | metabolic syndrome          | 0.437270       | 85    |
| 7     | increased prevalence        | 0.437177       | 19    |
| 8     | lifestyle interventions     | 0.434440       | 58    |
| 9     | insulin resistance          | 0.431953       | 85    |
| 10    | obese subjects              | 0.429812       | 13    |
| 11    | obese people                | 0.426166       | 13    |
| 12    | whole grains                | 0.423689       | 6     |
| 13    | underweight                 | 0.420408       | 14    |
| 14    | local food environments     | 0.416360       | 4     |
| 15    | dyslipidemia                | 0.415990       | 28    |

### Motivation

The idea started in the Epistemonikos database (epistemonikos.org), a database of scientific articles in health. Because normally in health/medicine the language used is complex. You can easily find keywords like:

 * asthma
 * heart failure
 * medial compartment knee osteoarthritis
 * preserved left ventricular systolic function
 * non-selective non-steroidal anti-inflammatory drugs

We tried some approaches to find those keywords, like ngrams, ngrams + tf-idf, identify entities, among others. But we didn't get really good results.

### Our approach

We found that tokenizing using stopwords + non word characters was really useful for "finding" the keywords. An example:

* input: "Timing of replacement therapy for acute renal failure after cardiac surgery"
* output: [
	"timing",
	"replacement therapy",
	"acute renal failure",
	"cardiac surgery"
]

So we basically split the text when we find:
 * a stopword
 * a non word character(/,!?. etc) (except from - and ')

That's it.


### References

Seem to be an old idea (2004):

*Mihalcea, Rada, and Paul Tarau. "Textrank: Bringing order into text." Proceedings of the 2004 conference on empirical methods in natural language processing. 2004.*

Reading an implementation of textrank, I realize they used stopwords to separate and create the graph. Then I though in using it as tokenizer for word2vec

As pointed by @deliprao in this [twitter thread](https://twitter.com/jeremyphoward/status/1094025901371621376). It's also used by Rake (2010):

*Rose, Stuart & Engel, Dave & Cramer, Nick & Cowley, Wendy. (2010). Automatic Keyword Extraction from Individual Documents. 10.1002/9780470689646.ch1.*

As noted by @astent in the Twitter thread, this concept is called chinking (chunking by exclusion)
[https://www.nltk.org/book/ch07.html#Chinking](https://www.nltk.org/book/ch07.html#Chinking)

### Multi-lingual
We worked in an implementation, that could be used in multiple languages. Of course not all languages are sutable for using this approach. We have tried with good results in English, Spanish and Portuguese (you need the stopwords for each language)

For more detail, take a look to the tokenizer here: [keywords_tokenizer.py](keywords_tokenizer.py)

## Try it online

You can try it [here](http://18.212.76.171/episte/) (takes time to load, lowercase only, doesn't work in mobile yet) MPV :)

These embedding were created using 827,341 title/abstract from @epistemonikos database.
With keywords that repeat at least 10 times. The total vocab is 349,080 keywords (really manageable number)

## Limitations

It's a fact that this method is not perfect. You are going to lose, keywords that cointain stopwords, like:
 * Vitamin A
 * Web of Science

As pointed out by [@peteskomoroch](https://twitter.com/peteskomoroch/status/1094036075247325184) there is other library [AutoPhrase](https://github.com/shangjingbo1226/AutoPhrase) that seem to deal with this (haven't try it yet)

## Vocab size

One of the main benefit of this method, is the size of the vocabulary. 
For example, using keywords that repeat at least 10 times, for the Epistemonikos dataset (827,341 title/abstract), we got the following vocab size:

| ngrams             | keywords  | comp    |
|--------------------|-----------|---------|
| 1                  | 127,824   | 36%     |
| 1,2                | 1,360,550 | 388%    |
| 1-3                | 3,204,099 | 914%    |
| 1-4                | 4,461,930 | 1,272%  |
| 1-5                | 5,133,619 | 1,464%  |
|                    |           |         |
| stopword tokenizer | 350,529   | 100%    |

More information regarding the comparison, take a look to the folder [analyze](analyze).

## Epistemonikos Example

### Get the data

```
mkdir -p data/inputs
wget "http://s3.amazonaws.com/episte-labs/episte_title_abstract.tsv.gz" -O data/inputs/episte_title_abstract.tsv.gz
```

### Install dependencies

```
pip install -r requirements.txt
```

### Train the model

Let's first use only 30,000 references to train the embeddings:
```
python keywords2vec.py -i data/inputs/episte_title_abstract.tsv.gz --column-numbers=2,3 --additional-stopwords="from,will,vs,versus,from,patient,patients,ci,md" --name="episte_30000" --sample=30000
```

> Step1: Tokenizing

> Step2: Reading keywords

> Step3: Calculate frequency

> Step4: Generate word2vec model

> Step5: Save vectors

> Step6: Save counter

### Try it

```
python try_keywords2vec.py -v data/experiments/episte_3000/word2vec.vec -n episte_30000 -p"obesity"
```

Finding similar keywords for "obesity"

| index | term                        | score          | count |
|-------|-----------------------------|----------------|-------|
| 0     | overweight                  | 0.500965       | 297   |
| 1     | obese individuals           | 0.479940       | 15    |
| 2     | obese                       | 0.470804       | 152   |
| 3     | hypertension                | 0.444629       | 838   |
| 4     | obese adults                | 0.444151       | 28    |
| 5     | bariatric surgery           | 0.441297       | 83    |
| 6     | metabolic syndrome          | 0.437270       | 85    |
| 7     | increased prevalence        | 0.437177       | 19    |
| 8     | lifestyle interventions     | 0.434440       | 58    |
| 9     | insulin resistance          | 0.431953       | 85    |
| 10    | obese subjects              | 0.429812       | 13    |
| 11    | obese people                | 0.426166       | 13    |
| 12    | whole grains                | 0.423689       | 6     |
| 13    | underweight                 | 0.420408       | 14    |
| 14    | local food environments     | 0.416360       | 4     |
| 15    | dyslipidemia                | 0.415990       | 28    |
| 16    | white caucasians            | 0.411259       | 4     |
| 17    | hyperlipidaemia             | 0.410208       | 9     |
| 18    | glucose tolerance           | 0.403859       | 6     |
| 19    | cardiovascular risk factors | 0.403232       | 60    |
| 20    | weight reduction            | 0.394117       | 44    |
| 21    | chronic diseases            | 0.390585       | 80    |
| 22    | pediatric type              | 0.390533       | 6     |
| 23    | body fat distribution       | 0.387237       | 3     |
| 24    | older age                   | 0.386911       | 26    |

## Server

You can start a server to play around with the data:
```
FLASK_APP=server/server.py VECTORS_PATH=server/models/episte_all_w10_s150 flask run
```
