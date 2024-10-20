import numpy as np


def get_external_similarity(identifiers, model):
    """
    For each identifier name, find the top three most similar names in the
    FastText model, select the most similar among them, and compute the median
    of these highest similarities for all identifiers. Returns the median of
    the highest similarity scores among the top three similar names for each
    identifier.
    """
    # Load the FastText model

    # List to store the highest similarity score for each identifier
    highest_similarities = []

    for identifier in identifiers:
        # Retrieve the top three most similar words and their cosine similarities
        similar_words = model.get_nearest_neighbors(identifier, k=3)

        # The first element has the highest similarity due to how get_nearest_neighbors works
        highest_similarity = similar_words[0][0] if similar_words else 0
        highest_similarities.append(highest_similarity)

    # Compute and return the median of the highest similarity scores
    median_similarity = np.median(highest_similarities) if highest_similarities else 0
    return median_similarity
