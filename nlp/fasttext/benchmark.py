import argparse
import fasttext
import pandas as pd
from rich.console import Console
import requests

from scipy.spatial.distance import cosine

console = Console()

LLM_MODEL = "deepseek-coder-v2:16b"


def rate_identifiers(name1, name2):
    prompt = f"""
    In this experiment, I will give you two source code identifiers to rate their relatedness.
    Example of related identifiers are: 'index' and 'idx', 'item' and 'record'.
    Rate how similar the identifiers '{name1}' and '{name2}' are from 1 to 10. Only reply with: I score it as <score>
    """

    prompt = f"""
    In this experiment, I will give you two source code identifiers to rate their similarity
    Example of similar identifiers are: 'min' and 'max', 'nextText' and 'prevText'.
    Rate how related identifiers '{name1}' and '{name2}' are from 1 to 10. Only reply with: I score it as <score>
    """

    url = "http://localhost:11434/api/generate"
    payload = {"model": LLM_MODEL, "prompt": prompt, "stream": False}
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        try:
            json = response.json()['response']
            console.print(json)
            classified_type = json

            for typ in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
                if typ in classified_type:
                    console.print(f'Classified {name1} and {name2} as {typ}')
                    return float(typ)
        except:
            console.print(f"Failed to parse response LLM: {json}")
            return None
    else:
        console.print(f"Request failed with status code {response.status_code}")
        return None



def add_cosine_similarity_to_csv(csv_file, fasttext_model, output_file):
    df = pd.read_csv(csv_file)

    def calculate_similarity(row):
        vec1 = fasttext_model.get_word_vector(row["id1"])
        vec2 = fasttext_model.get_word_vector(row["id2"])
        return 1 - cosine(vec1, vec2)

    df["Cosine_Similarity"] = df.apply(calculate_similarity, axis=1)
    df.to_csv(output_file, index=False)


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-m", required=True, help="path to fastText model")
    # args = parser.parse_args()
    model = fasttext.load_model("build/models/ft_19M_100x1000_5ws.bin")

    # model = fasttext.load_model(args.m)
    add_cosine_similarity_to_csv("small_pair_wise.csv", model, "small_.csv")
    add_cosine_similarity_to_csv("medium_pair_wise.csv", model, "medium_.csv")
    add_cosine_similarity_to_csv("large_pair_wise.csv", model, "large_.csv")