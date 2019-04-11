# Comparing vocab size

We generate a quick comparison with the size of the vocab, using the stopword tokenizer vs ngrams. To do this, we used bigquery.
You can take a look to the dataset [here](https://bigquery.cloud.google.com/dataset/api-project-380745743806:epistemonikos)

| ngrams             | keywords  | comp    |
|--------------------|-----------|---------|
| 1                  | 127,824   | 36%     |
| 1,2                | 1,360,550 | 388%    |
| 1-3                | 3,204,099 | 914%    |
| 1-4                | 4,461,930 | 1,272%  |
| 1-5                | 5,133,619 | 1,464%  |
|                    |           |         |
| stopword tokenizer | 350,529   | 100%    | 

## Reproduce
If you wanted to reproduce the results

### Get the data
cd to this folder
```
mkdir -p ../data/inputs
wget "http://s3.amazonaws.com/episte-labs/episte_title_abstract.tsv.gz" -O ../data/inputs/episte_title_abstract.tsv.gz
```

### Get all keywords

```
python compare_to_ngrams.py ../data/inputs/episte_title_abstract.tsv.gz| gzip > ../data/all_keywords.tsv.gz
```

### upload to bigquery
```
gsutil -o GSUtil:parallel_composite_upload_threshold=150M cp "data/all_found.tsv.gz" gs://episte-lab/all_tokens.tsv.gz

bq mk "api-project-380745743806:epistemonikos.all_keywords" tokenizer_name:string,keyword:string

bq load --replace --max_bad_records=40000 --field_delimiter="\t" --source_format=CSV "api-project-380745743806:epistemonikos.all_keywords" gs://episte-lab/all_tokens.tsv.gz
```

### Count

In bigquery, execute the following query, using standard query language, and as destination table we set _epistemonikos.count_keywords_ table.

```
SELECT tokenizer_name, keyword, count(*) as repeat_count
FROM `api-project-380745743806.epistemonikos.all_keywords`
GROUP BY tokenizer_name, keyword
```

Then we query and set as destination table _epistemonikos.vocab_size_ with append, and changing the number 1 for 2, then 3, and so (a better query is needed later):

```
SELECT tokenizer_name, 1 as min_repeat, count(*) as vocab_size
FROM `api-project-380745743806.epistemonikos.count_keywords`
WHERE repeat_count >= 1
GROUP BY tokenizer_name
ORDER BY vocab_size DESC
```

Now you can get the vocab_size, and get a CSV like [this](vocab_size_results.csv):
```
SELECT *
FROM `api-project-380745743806.epistemonikos.vocab_size`
ORDER BY min_repeat ASC, vocab_size DESC
LIMIT 1000
```

## The data
The data is public [here](https://bigquery.cloud.google.com/dataset/api-project-380745743806:epistemonikos)

You can play around.