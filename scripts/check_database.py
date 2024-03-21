import argparse
from wiki_graph_kb.WikiGraphKB import WikiGraphKB


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", type=str, default="bolt://localhost:7687") # bolt://ist-compute-1-001:7687
    parser.add_argument("--username", type=str, default="neo4j")
    parser.add_argument("--password", type=str, default="panuthept")
    args = parser.parse_args()

    URI = args.uri
    AUTH = (args.username, args.password)
    kb = WikiGraphKB(uri=URI, auth=AUTH)
    response = kb.query("MATCH (n) RETURN count(n)")
    print(f"Number of existing nodes: {response[0]["count(n)"]}")