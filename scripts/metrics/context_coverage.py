import numpy as np
from gensim import corpora, models, similarities


def get_context_coverage(texts):
    """
    Calculate the context coverage for terms in a collection of documents.
    Returns a dictionary of terms with their context coverage scores.
    """

    # Create a dictionary and corpus
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    # Initialize an LSI model
    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=100)

    # Create a similarity index
    index = similarities.MatrixSimilarity(lsi[corpus])

    # Calculate context coverage for each unique term in the dictionary
    context_coverage = {}
    for word_id, word in dictionary.items():
        relevant_docs_indices = [i for i, doc in enumerate(texts) if word in doc]
        if len(relevant_docs_indices) < 2:
            # Need at least two documents to calculate similarity
            continue
        
        # Calculate similarities between documents containing the word
        sims = []
        for i in range(len(relevant_docs_indices)):
            for j in range(i + 1, len(relevant_docs_indices)):
                sims.append(index[lsi[corpus[relevant_docs_indices[i]]]][relevant_docs_indices[j]])
        
        # Compute context coverage as defined
        N = len(sims)
        if N > 0:
            CC = (1 - (1 / N)) * np.sum(sims)
            context_coverage[word] = CC

    return context_coverage

