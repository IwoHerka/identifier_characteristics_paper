import numpy as np
from gensim import corpora, models, similarities
from rich.console import Console
from sklearn.preprocessing import normalize

console = Console()


def get_context_coverage(texts, target_words):
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    console.print(f"Starting to train LSI model", style="yellow")

    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=100)

    index = similarities.MatrixSimilarity(lsi[corpus])

    console.print(f"LSI model trained", style="green")

    similarity_cache = {}
    doc_sim_cache = {}

    context_coverage_scores = {}

    for target_word in target_words:
        if target_word not in dictionary.token2id:
            context_coverage_scores[target_word] = 0
            continue

        word_id = dictionary.token2id[target_word]
        relevant_docs_indices = [
            i for i, text in enumerate(texts) if target_word in text
        ]

        if len(relevant_docs_indices) < 2:
            context_coverage_scores[target_word] = 0
            continue

        similarities_list = []
        for i, doc_idx_1 in enumerate(relevant_docs_indices[:10]):
            if doc_idx_1 not in doc_sim_cache:
                doc_sim_cache[doc_idx_1] = index[lsi[corpus[doc_idx_1]]]

            sim_vector_1 = doc_sim_cache[doc_idx_1]

            for doc_idx_2 in relevant_docs_indices[i + 1 :]:
                pair = (doc_idx_1, doc_idx_2)
                if pair not in similarity_cache:
                    sim = sim_vector_1[doc_idx_2]
                    similarity_cache[pair] = sim if sim > 0 else 0
                similarities_list.append(similarity_cache[pair])

        N = len(similarities_list)

        if N > 0:
            normalized_cc = np.mean(similarities_list)
        else:
            normalized_cc = 0

        context_coverage_scores[target_word] = normalized_cc

    return context_coverage_scores
