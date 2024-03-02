# WikiGraphKB
WikiGraphKB is a knowledge graph database that combines Wikipedia with Wikidata.

## Wikipedia Processing
- Download a [Wikipedia dump](https://dumps.wikimedia.org/enwiki/20240220/), e.g., [enwiki-20240220-pages-articles-multistream.xml.bz2](https://dumps.wikimedia.org/enwiki/20240220/enwiki-20240220-pages-articles-multistream.xml.bz2).
- Extract text contents from the downloaded dump with [WikiExtractor](https://github.com/attardi/wikiextractor/tree/master).
```python
python -m wikiextractor.WikiExtractor enwiki-20240220-pages-articles-multistream.xml.bz2 \
--output ./extracted_wikipedia \
--json \
--links
```
- Run `process_wikipedia.py` to clean the text contents, extract hyperlinks, and create index.
```python
python -m process_wikipedia --input ./extracted_wikipedia --output ./processed_wikipedia
```

- Run `wikipedia_statistic.py` to check the statistics of the processed wikipedia corpus, e.g., number of pages and hyperlinks.
```python
python -m wikipedia_statistic --input ./processed_wikipedia
```
