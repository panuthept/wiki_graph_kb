# WikiGraphKB
WikiGraphKB is a knowledge graph database that combines Wikipedia with Wikidata.

![WikiGraphKB](https://github.com/panuthept/wiki_graph_kb/assets/28400944/08e9476c-1ced-4b7d-8d2a-1b715ff1f723)

## Wikipedia Processing
- Download a [Wikipedia dump](https://dumps.wikimedia.org/enwiki/20240220/), e.g., [enwiki-20240220-pages-articles-multistream.xml.bz2](https://dumps.wikimedia.org/enwiki/20240220/enwiki-20240220-pages-articles-multistream.xml.bz2).
- Extract contents from the downloaded dump with [WikiExtractor](https://github.com/attardi/wikiextractor/tree/master) (takes 5 hrs on 10 CPUs).
```python
python -m wikiextractor.WikiExtractor
./enwiki-20240220-pages-articles-multistream.xml.bz2 \
--output ./extracted_wikipedia \  # 24 GB
--json \
--links
```
- Run `process_wikipedia.py` to clean the documents, and extract paragraphs and hyperlinks (takes 19 mins on 10 CPUs).
```python
python -m process_wikipedia --input ./extracted_wikipedia --output ./wikipedia_corpus  # 31 GB
```

The `wikipedia_corpus` can be downloaded using this [link]().

## Wikidata Processing
- Download a [Wikidata dump](https://www.wikidata.org/wiki/Wikidata:Database_download/en), e.g., [wikidata-lastest-all.json.gz](https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.gz).
- Download a Wikidata's properties dump from [Propbrowse](https://hay.toolforge.org/propbrowse/).
```
wget https://hay.toolforge.org/propbrowse/props.json
```
- Extract contents from the downloaded dump with [simple-wikidata-db](https://github.com/neelguha/simple-wikidata-db) (takes 15 hrs on 10 CPUs).
```python
python -m simple_wikidata_db.preprocess_dump \
--input_file ./wikidata-lastest-all.json.bz2 \
--out_dir ./extracted_wikidata \  # 250 GB
--language_id en
```
- Run `process_wikidata.py` to aggregate necessary data.
```python
python -m process_wikidata --input ./extracted_wikidata --output ./wikidata_corpus  # 31 GB
```

The `wikidata_corpus` can be downloaded using this [link]().

## Using WikiGraphKB
`WikiGraphKB` is based on [Neo4j](https://github.com/neo4j/neo4j?tab=readme-ov-file) database, it will automatically build the database given the paths to [wikipedia corpus]() and [wikidata corpus]().
```python
kb = WikiGraphKB(uri="<URI for Neo4j database>", auth=("<Username>", "<Password>"))
```
To create a new collection, use the `new_collection()` method.
```python
kb.new_collection("WikiGraphKB20240220", wikipedia_corpus_path, wikidata_corpus_path)
```
To load the existing collection, use the `load_collection()` method or specify during the initial.
```python
kb.load_collection("WikiGraphKB20240220")
# or
kb = WikiGraphKB(uri="<URI for Neo4j database>", auth=("<Username>", "<Password>"), collection="WikiGraphKB20240220")
```
To update the database, use the `add()`, `edit()`, and `delete()` methods.
```python
kb.add(Document(id="12", title="Anarchism", description="Political philosophy and movement"))     # Add a document
kb.edit(Document(id="12", title="Anarchism", description="Some new description"))                 # Edit a document
kb.delete(Document(id="12"))                                                                      # Remove a document
```
To retrieve items, use the `query()` method.
```python
document = kb.query("document", id="12")                                     # Retrieve the document whose id is '12'
documents = kb.query("documents", title="Anarchism")                         # Retrieve all documents whose title is 'Anarchism'
title, desc = kb.query("document", id="12", key=["title", "description"])    # Retrieve the title and description of the document whose id is '12'
entity = kb.query("document", id="12", key="refers_to")                      # Retrieve the entity of the document whose id is '12'
passages = kb.query("document", id="12", key="paragraph")                    # Retrieve all passages in the document whose id is '12'
passages = kb.query("passages", id=["12_0", "12_1"])                         # Retrieve the first and second passages in the document whose id is '12'
passage = kb.query("passage", id="12_0")                                     # Retrieve the first passage in the document whose id is '12'
entities = kb.query("passage", id="12_0", key="mentions")                    # Retrieve all entities mentioned in the passage whose id is '12_0'
```
`WikiGraphKB` also supports vector search, using the `embeddings` and `top_k` arguments.
```python
kb.encode()                                                                  # Encode knowledge using default encoder model
documents = kb.query("documents", embeddings=embeddings, top_k=5)            # Retrieve top-5 documents
```
