import os
import re
import json
import argparse
from tqdm import tqdm
from html import unescape
from urllib.parse import unquote
from collections import defaultdict


def remove_template_styles(text):
    remaining_contents = []
    for i, content in enumerate(text.split("<templatestyles src=")):
        if i == 0:
            remaining_contents.append(content)
            continue
        remaining_content = content.split("/>")[-1]
        remaining_contents.append(remaining_content)
    remaining_text = "".join(remaining_contents).replace("\n\n", "\n")
    return remaining_text


def extract_hyperlinks(text):
    """
    Examples of hyperlinks syntax:
    - <a href=[WIKIPEDIA_TITLE]>[MENTION_SURFACE]</a>
    """
    acc_start = 0
    hyperlinks = []
    remaining_text = ""
    # remaining_contents = []
    # Clean content
    text = text.replace("</a>s", "s</a>")
    text = text.replace("<br>", "")
    text = text.replace("»", ">>")
    text = text.replace("«", "<<")
    for i, content in enumerate(text.split("<a href=")):
        if i == 0:
            acc_start += len(content)
            remaining_text += content
            # remaining_contents.append(content)
            continue
        if len(content.split("</a>")) < 2:
            if len(content.split(">")) < 2:
                print("Fail to split entity_mention and remaining_content:")
                print(content)
                print("-" * 50)
                return None, None
            remaining_content = re.split(">", content, 1)[1]
            acc_start += len(remaining_content)
            remaining_text += remaining_content
            # remaining_contents.append(remaining_content)
        else:
            entity_mention, remaining_content = re.split("</a>", content, 1)
            if len(entity_mention.split(">")) < 2:
                print("Fail to split wikipedia_title and mention_surface:")
                print(entity_mention)
                print("-" * 50)
                return None, None
            wikipedia_title, mention_surface = re.split(">", entity_mention, 1)
            hyperlink = {
                "start": acc_start,
                "length": len(mention_surface),
                "mention_surface": mention_surface,
                "wikipedia_title": wikipedia_title[1:-1].lower(),
            }
            remaining_content = mention_surface + remaining_content
            acc_start += len(remaining_content)
            remaining_text += remaining_content
            # remaining_contents.append(remaining_content)
            assert remaining_text[hyperlink["start"]:hyperlink["start"] + hyperlink["length"]] == hyperlink["mention_surface"], f'Mention index error: {remaining_text[hyperlink["start"]:hyperlink["start"] + hyperlink["length"]]} != {hyperlink["mention_surface"]}'
            hyperlinks.append(hyperlink)
    # remaining_text = "".join(remaining_contents)
    return remaining_text, hyperlinks


def process_wikipedia(input_dir, output_dir):
    os.makedirs(os.path.join(output_dir, "corpus"), exist_ok=True)

    id2path = {}
    id2title = {}
    title2ids = defaultdict(set)
    for folder in tqdm(os.listdir(input_dir)):
        if folder == ".DS_Store": 
            continue
        for file in os.listdir(os.path.join(input_dir, folder)):
            if file == ".DS_Store": 
                continue
            # print(f"{folder}/{file}")
            with open(os.path.join(input_dir, folder, file), "r") as input_f:
                processed_data = {}
                for line in input_f:
                    doc = json.loads(line)
                    text = doc["text"]
                    text = unescape(text)
                    text = unquote(text)
                    if len(text.split("\n")) == 1:
                        continue
                    description, content = re.split("\n", text, 1)
                    if "href=" in description:
                        # Some pages do not have a short description
                        description = ""
                        content = description + content
                    if text == "":
                        continue
                    # Clean text
                    content = remove_template_styles(content)
                    # content = remove_externallikes(content)
                    content, hyperlinks = extract_hyperlinks(content)
                    # Save fail cases
                    if hyperlinks is None:
                        os.makedirs(os.path.join(output_dir, "fail_cases", folder), exist_ok=True)
                        with open(os.path.join(output_dir, "fail_cases", folder, file), "a") as output_f:
                            output_f.write(f"{line}\n")
                        continue
                    # Update processed data
                    doc_title = doc["title"].lower()
                    doc_id = doc["id"]
                    doc_url = doc["url"]
                    doc_revid = doc["revid"]
                    processed_data[doc_id] = {
                        "title": doc_title,
                        "description": description,
                        "content": content,
                        "hyperlinks": hyperlinks,
                        "metadata": {"id": doc_id, "url": doc_url, "revid": doc_revid}
                    }
                    # Update index
                    title2ids[doc_title].add(doc_id)
                    if doc_id in id2path: 
                        raise ValueError(f"Found duplicated document ids: {doc_id} >> {f"{folder}_{file.replace('wiki_', '')}.json"} and {id2path[doc_id]}")
                    id2path[doc_id] = f"{folder}_{file.replace('wiki_', '')}.json"
                    if doc_id in id2title: 
                        raise ValueError(f"Found duplicated document ids: {doc_id} >> {doc_title} and {id2title[doc_id]}")
                    id2title[doc_id] = doc_title
                # Write processed data
                with open(os.path.join(output_dir, "corpus", f"{folder}_{file.replace('wiki_', '')}.json"), "w") as output_f:
                    json.dump(processed_data, output_f)
    # Write index
    title2ids = {key: list(values) for key, values in title2ids.items()}
    with open(os.path.join(output_dir, "title2ids.json"), "w") as output_f:
        json.dump(title2ids, output_f)
    with open(os.path.join(output_dir, "id2title.json"), "w") as output_f:
        json.dump(id2title, output_f)
    with open(os.path.join(output_dir, "id2path.json"), "w") as output_f:
        json.dump(id2path, output_f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="input file")
    parser.add_argument("--output", help="output file")
    args = parser.parse_args()

    process_wikipedia(args.input, args.output)


if __name__ == "__main__":
    main()