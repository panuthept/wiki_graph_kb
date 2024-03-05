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
- Run `process_wikipedia.py` to clean the documents, split documents, and extract hyperlinks.
```python
python -m process_wikipedia --input ./extracted_wikipedia --output ./wikipedia_corpus
```

The finished Wikipedia corpus can be downloaded using this [link]().

## Wikidata Processing

## Using WikiGraphKB
Create the `WikiGraphKB` object given the paths to `wikipedia_corpus` and `wikidata_corpus`.
```python
kb = WikiGraphKB(wikipedia_corpus_path, wikidata_corpus_path)
```
To retrieve items, using the `query()` method.
```python
document = kb.query("document", id="12")                                     # Retrieve the document whose id is '12'
documents = kb.query("documents", title="Anarchism")                         # Retrieve all documents whose title is 'Anarchism'
title, desc = kb.query("document", id="12", key=["title", "description"])    # Retrieve title and description of the document whose id is '12'
entity = kb.query("document", id="12", key="refers_to")                      # Retrieve the entity of the document whose id is '12'
passages = kb.query("document", id="12", key="paragraph")                    # Retrieve all passages in the document whose id is '12'
passages = kb.query("passages", id=["12_0", "12_1"])                         # Retrieve the first and second passages in the document whose id is '12'
passage = kb.query("passage", id="12_0")                                     # Retrieve the first passage in the document whose id is '12'
entities = kb.query("passage", id="12_0", key="mentions")                    # Retrieve all entities mentioned in the passage whose id is '12_0'
```
`WikiGraphKB` also support vector search by providing `embeddings` and `top_k` arguments.
```python
kb.encode()                                                                  # Encode knowledge using default encoder model
documents = kb.query("documents", embeddings=embeddings, top_k=5)            # Retrieve top-5 documents
```
To update the database, using the `add()`, `update()`, `delete()` methods.
```python
kb.add(Document(id="12", title="Anarchism", description="Political philosophy and movement"))     # Add a document
kb.update(Document(id="12", title="Anarchism", description="Some new description"))               # Update a document
kb.delete(Document(id="12"))                                                                      # Remove a document
```
