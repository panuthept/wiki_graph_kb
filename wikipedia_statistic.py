import os
import json
import argparse
from tqdm import tqdm


def wikipedia_statistic(input_dir):
    id2title = json.load(open(os.path.join(input_dir, "id2title.json"), "r"))
    title2ids = json.load(open(os.path.join(input_dir, "title2ids.json"), "r"))

    # Count fail-cases
    failed_cases = 0
    for folder in tqdm(os.listdir(os.path.join(input_dir, "fail_cases"))):
        if folder == ".DS_Store": 
            continue
        for file in os.listdir(os.path.join(input_dir, "fail_cases", folder)):
            if file == ".DS_Store": 
                continue
            with open(os.path.join(input_dir, "fail_cases", folder, file), "r") as input_f:
                for line in input_f:
                    if line == "":
                        continue
                    failed_cases += 1
    # Count hyperlinks
    hyperlink_count = 0
    failed_hyperlink_count = 0
    for file in tqdm(os.listdir(os.path.join(input_dir, "corpus"))):
        if file == ".DS_Store": 
            continue
        with open(os.path.join(input_dir, "corpus", file), "r") as input_f:
            for line in input_f:
                if line == "":
                    continue
                docs = json.loads(line)
                for doc in docs.values():
                    for hyperlink in doc["hyperlinks"]:
                        hyperlink_count += 1
                        if hyperlink["wikipedia_title"].lower() not in title2ids:
                            failed_hyperlink_count += 1
    # Count duplicate title documents
    duplicated_title_count = 0
    for title, ids in title2ids.items():
        if len(ids) > 1:
            print(f"{title} >> {ids}")
            duplicated_title_count += len(ids)
    print(f"Number of success documents: {len(id2title)} / {len(id2title) + failed_cases} ({round(len(id2title) / (len(id2title) + failed_cases) * 100, 4)}%)")
    print(f"Number of success hyperlinks: {hyperlink_count - failed_hyperlink_count} / {hyperlink_count} ({round((hyperlink_count - failed_hyperlink_count) / hyperlink_count * 100, 4)}%)")
    print(f"Number of duplicated title documents: {duplicated_title_count} / {len(id2title)} ({round(duplicated_title_count / len(id2title) * 100, 4)}%)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="input file")
    args = parser.parse_args()

    wikipedia_statistic(args.input)


if __name__ == "__main__":
    main()