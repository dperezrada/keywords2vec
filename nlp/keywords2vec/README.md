# Keywords2vec

## Main idea
To generate a word2vec model, but using keywords instead of one word.

### Motivation
The idea started in the Epistemonikos database (epistemonikos.org), a database of scientific articles in health. Because normally in health/medicine the language used is complex. You can easily find keywords like:

 * asthma
 * heart failure
 * medial compartment knee osteoarthritis
 * preserved left ventricular systolic function
 * non-selective non-steroidal anti-inflammatory drugs

We tried some approaches to find those keywords, like ngrams, ngrams + tf-idf, identify entities, within others. But we didn't got really good results.

### Our approach

We found that tokenizing using stopwords + non word characters, was really usefull for "finding" the keywords. An example:

* input: "Timing of replacement therapy for acute renal failure after cardiac surgery"
* output: [
	"timing",
	"replacement therapy",
	"acute renal failure",
	"cardiac surgery"
]

So we basically split the text when we find:
 * a stopword
 * a non word character (except from - and ')

That's it.


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

Lets first use only 30,000 references to train, and
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

You can start a server to play around with the data.

```
FLASK_APP=server/server.py VECTORS_PATH=server/models/episte_all_w10_s150 flask run
```
