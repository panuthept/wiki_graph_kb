# WikiGraphKB
WikiGraphKB is a knowledge graph database that combines Wikipedia with Wikidata.

![WikiGraphKB](https://github.com/panuthept/wiki_graph_kb/assets/28400944/e41187e4-48d7-40ae-a212-257b451cded3)


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
- Run `wikipedia_statistic.py` to observe the statistics of the processed Wikipedia corpus, e.g., number of pages and hyperlinks.
```python
python -m wikipedia_statistic --input ./processed_wikipedia
```

The finished Wikipedia corpus can be downloaded using this [link]().

## Wikidata Processing

## Using WikiGraphKB
The `WikiGraphKB` class will automatically generate the graph database given the `wikipedia corpus` and `wikidata corpus`.
```python
kb = WikiGraphKB(wikipedia_corpus_path, wikidata_corpus_path)
```
To retrieve items, using the `retrieve()` method.
```python
document = kb.retrieve(query=Query(type="document", id="12"))                                     # Retrieve the document whose id is '12'
documents = kb.retrieve(query=Query(type="documents", title="Anarchism"))                         # Retrieve all documents whose title is 'Anarchism'
title, desc = kb.retrieve(query=Query(type="document", id="12", keys=["title", "description"]))   # Retrieve title and description of the document whose id is '12'
passage = kb.retrieve(query=Query(type="passage", id="12_0"))                                     # Retrieve the first passage in the document whose id is '12'
passages = kb.retrieve(query=Query(type="passages", id="12", keys="paragraph"))                   # Retrieve all passages in the document whose id is '12'
```
To update the database, using the `add()`, `update()`, `delete()` methods.
```python
kb.add(Document(id="12", title="Anarchism", description="Political philosophy and movement"))     # Add a document
kb.update(Document(id="12", title="Anarchism", description="Some new description"))               # Update a document
kb.delete(Document(id="12"))                                                                      # Remove a document
```
