# WikiGraphKB
WikiGraphKB is a knowledge graph database that combines Wikipedia with Wikidata.

![WikiGraphKB](https://github.com/panuthept/wiki_graph_kb/assets/28400944/e41187e4-48d7-40ae-a212-257b451cded3)


## Wikipedia Processing
- Download a [Wikipedia dump](https://dumps.wikimedia.org/enwiki/20240220/), e.g., [enwiki-20240220-pages-articles-multistream.xml.bz2](https://dumps.wikimedia.org/enwiki/20240220/enwiki-20240220-pages-articles-multistream.xml.bz2).
- Extract contents from the downloaded dump with [WikiExtractor](https://github.com/attardi/wikiextractor/tree/master).
```python
python -m wikiextractor.WikiExtractor
./enwiki-20240220-pages-articles-multistream.xml.bz2 \
--output ./extracted_wikipedia \
--json \
--links
```
- Run `process_wikipedia.py` to clean the documents, split documents, extract hyperlinks, and create index.
```python
python -m process_wikipedia --input ./extracted_wikipedia --output ./wikipedia_corpus
```

The finished Wikipedia corpus can be downloaded using this [link]().

## Wikidata Processing
- Download a [Wikidata dump](https://www.wikidata.org/wiki/Wikidata:Database_download/en), e.g., [wikidata-lastest-all.json.gz](https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.gz).
- Extract contents from the downloaded dump with [simple-wikidata-db](https://github.com/neelguha/simple-wikidata-db).
```python
python -m simple_wikidata_db.preprocess_dump \
--input_file ./wikidata-lastest-all.json.bz2 \
--out_dir ./wikidata_corpus \
--language_id en
```

the finished Wikidata corpus can be downloaded using this [link]().

## Using WikiGraphKB
`WikiGraphKB` is based on [Neo4j](https://github.com/neo4j/neo4j?tab=readme-ov-file) database, it will automatically build the database given the paths to [wikipedia corpus]() and [wikidata corpus]().
```python
kb = WikiGraphKB(uri="<URI for Neo4j database>", auth=("<Username>", "<Password>"))
```
To create the a new collection, using the `new_collection()` method.
```python
kb.new_collection("WikiGraphKB_20240220", wikipedia_corpus_path, wikidata_corpus_path)
```
To load the existing collection, using the `load_collection()` method.
```python
kb.load_collection("WikiGraphKB_20240220")
```
To update the database, using the `add()`, `edit()`, `delete()` methods.
```python
kb.add(Document(id="12", title="Anarchism", description="Political philosophy and movement"))     # Add a document
kb.edit(Document(id="12", title="Anarchism", description="Some new description"))                 # Edit a document
kb.delete(Document(id="12"))                                                                      # Remove a document
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
`WikiGraphKB` also support vector search, using the `embeddings` and `top_k` arguments.
```python
kb.encode()                                                                  # Encode knowledge using default encoder model
documents = kb.query("documents", embeddings=embeddings, top_k=5)            # Retrieve top-5 documents
```
