import sys
from gensim.models import Word2Vec


def load_model(model_file):
    # Load the trained Word2Vec model
    model = Word2Vec.load(model_file)
    return model


def test_model(model):
    # Test the model by finding similar words
    try:
        # Find similar words to 'example'
        similar_words = model.wv.most_similar("example", topn=10)
        print("Most similar words to 'example':")
        for word, similarity in similar_words:
            print(f"{word}: {similarity}")

        # Find the word that doesn't match in a list
        odd_one_out = model.wv.doesnt_match(["breakfast", "lunch", "dinner", "cat"])
        print(f"The word that doesn't match is: {odd_one_out}")

        # Perform a word analogy task
        analogy = model.wv.most_similar(
            positive=["king", "woman"], negative=["man"], topn=1
        )
        print(f"King is to man as what is to woman? - {analogy[0][0]}")

    except KeyError as e:
        print(f"Error: {e}")
        print(
            "The word might not be in the vocabulary. Please test with a word that exists in the trained corpus."
        )


def main(model_file):
    model = load_model(model_file)
    test_model(model)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <model_file>")
        sys.exit(1)

    model_file = sys.argv[1]
    main(model_file)
