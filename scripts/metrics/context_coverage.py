import numpy as np
from gensim import corpora, models, similarities


def get_context_coverage(texts, target_words):
    """
    Calculate the normalized context coverage for a specific word in a given collection of documents.
    Returns the normalized context coverage score for the target word, scaled between 0 and 1.
    """

    # Create a dictionary and corpus
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    # Initialize an LSI model
    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=100)

    # Create a similarity index
    index = similarities.MatrixSimilarity(lsi[corpus])

    for target_word in target_words:
        # Check if the target word is in the dictionary
        if target_word not in dictionary.token2id:
            raise ValueError("Target word not found in the texts.")

        # Find documents that contain the target word
        word_id = dictionary.token2id[target_word]
        # This can be optimized
        relevant_docs_indices = [i for i, doc in enumerate(texts) if target_word in doc]

        if len(relevant_docs_indices) < 2:
            # Need at least two documents to calculate similarity
            return 0

        # Calculate similarities between documents containing the target word
        sims = []
        for i in range(len(relevant_docs_indices)):
            for j in range(i + 1, len(relevant_docs_indices)):
                sim = index[lsi[corpus[relevant_docs_indices[i]]]][
                    relevant_docs_indices[j]
                ]
                sims.append(sim if sim > 0 else 0)  # Ensure non-negative similarities

        # Compute normalized context coverage
        N = len(sims)
        if N > 0:
            normalized_CC = np.mean(
                sims
            )  # Directly calculates the average of similarities
            yield (target_word, normalized_CC)
        else:
            yield (target_word, 0)
