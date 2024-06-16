import argparse
import pandas as pd

from scipy.spatial.distance import cosine


def add_cosine_similarity_to_csv(csv_file, fasttext_model, output_file):
    df = pd.read_csv(csv_file)

    def calculate_similarity(row):
        vec1 = fasttext_model.get_word_vector(row["id1"])
        vec2 = fasttext_model.get_word_vector(row["id2"])
        return 1 - cosine(vec1, vec2)

    df["Cosine_Similarity"] = df.apply(calculate_similarity, axis=1)
    df.to_csv(output_file, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", required=True, help="path to fastText model")
    args = parser.parse_args()

    model = fasttext.load_model(args.m)
    add_cosine_similarity_to_csv("small_pair_wise.csv", model, "small_.csv")
    add_cosine_similarity_to_csv("medium_pair_wise.csv", model, "medium_.csv")
    add_cosine_similarity_to_csv("large_pair_wise.csv", model, "large_.csv")
