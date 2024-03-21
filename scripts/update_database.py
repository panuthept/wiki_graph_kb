import argparse
from wiki_graph_kb.WikiGraphKB import WikiGraphKB


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", type=str, default="bolt://localhost:7687") # bolt://ist-compute-1-001:7687
    parser.add_argument("--username", type=str, default="neo4j")
    parser.add_argument("--password", type=str, default="panuthept")
    parser.add_argument("--start_index", type=int, default=0)
    parser.add_argument("--end_index", type=int, default=-1)
    args = parser.parse_args()

    URI = args.uri
    AUTH = (args.username, args.password)
    kb = WikiGraphKB(uri=URI, auth=AUTH)
    kb.update_collection(
        wikidata_corpus_path="./wikidata_corpus",
        wikidata_range=(args.start_index, args.end_index)
    )