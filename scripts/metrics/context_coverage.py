from gensim import corpora, models, similarities
from sklearn.preprocessing import normalize
import numpy as np
from rich.console import Console

console = Console()


def get_context_coverage(texts, target_words):
    """
    Calculate the normalized context coverage score for each target word.

    Args:
        texts (list of list of str): A list of tokenized texts.
        target_words (list of str): A list of target words to analyze.

    Returns:
        dict: A dictionary where keys are target words, and values are their normalized context coverage scores.
    """
    # Create a dictionary and corpus
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    console.print(f"Starting to train LSI model", style="yellow")

    # Initialize an LSI model
    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=100)

    # Create a similarity index for the corpus
    index = similarities.MatrixSimilarity(lsi[corpus])

    console.print(f"LSI model trained", style="green")

    # Cache for pairwise similarities
    similarity_cache = {}

    # Store context coverage scores
    context_coverage_scores = {}

    for target_word in target_words:
        # Check if the target word exists in the dictionary
        if target_word not in dictionary.token2id:
            context_coverage_scores[target_word] = 0
            continue

        # Get the word ID and find texts containing the target word
        word_id = dictionary.token2id[target_word]
        relevant_docs_indices = [i for i, text in enumerate(texts) if target_word in text]

        # If fewer than 2 documents contain the word, context coverage is undefined
        if len(relevant_docs_indices) < 2:
            context_coverage_scores[target_word] = 0
            continue

        # Calculate pairwise similarities between relevant documents
        similarities_list = []
        for i, doc_idx_1 in enumerate(relevant_docs_indices[:10]):
            for doc_idx_2 in relevant_docs_indices[i + 1:]:
                pair = (doc_idx_1, doc_idx_2)
                if pair not in similarity_cache:
                    sim = index[lsi[corpus[doc_idx_1]]][doc_idx_2]
                    similarity_cache[pair] = sim if sim > 0 else 0
                similarities_list.append(similarity_cache[pair])

        # Compute normalized context coverage as the average similarity
        N = len(similarities_list)
        if N > 0:
            normalized_cc = np.mean(similarities_list)
        else:
            normalized_cc = 0

        context_coverage_scores[target_word] = normalized_cc

    return context_coverage_scores
