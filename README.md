# WikiGraphKB
WikiGraphKB is a knowledge base that combine Wikipedia and Wikidata, allowing multi-hop retrieval over Wikipedia pages based on entities.

## Wikipedia Processing
- Download a [Wikipedia dump](https://dumps.wikimedia.org/enwiki/20240220/), e.g., [enwiki-20240220-pages-articles-multistream.xml.bz2](https://dumps.wikimedia.org/enwiki/20240220/enwiki-20240220-pages-articles-multistream.xml.bz2).
- Extract text contents from the downloaded dump with [WikiExtractor](https://github.com/attardi/wikiextractor/tree/master).
```python
python -m wikiextractor.WikiExtractor enwiki-20240220-pages-articles-multistream.xml.bz2 \
--output <your_output_dir> \
--json \
--links
```
- Run `process_wikipedia.py` to clean the text contents, extract hyperlinks, and create index.

