file = "build/unigrams.txt"


def load_word_frequencies(file_path):
    # Initialize an empty dictionary to store word frequencies
    word_frequencies = {}
    # Initialize a variable to hold the sum of all occurrences
    total_occurrences = 0

    # Open the file at the given path
    with open(file_path, "r") as file:
        # Read the file line by line
        for line in file:
            # Split each line into a word and its occurrence count
            parts = line.split()
            # Safety check to ensure there are exactly two parts
            if len(parts) != 2:
                continue

            word, occurrences = parts[0], parts[1]
            try:
                # Convert the occurrences to an integer
                occurrences = int(occurrences)
            except ValueError:
                # Skip this line if the occurrences part is not an integer
                continue

            # Add or update the word in the dictionary
            if word in word_frequencies:
                word_frequencies[word] += occurrences
            else:
                word_frequencies[word] = occurrences

            # Add the occurrences to the total sum
            total_occurrences += occurrences

    return word_frequencies, total_occurrences


# frequencies, total = load_word_frequencies(file)
# print("Frequencies:", frequencies)
# print("Total Sum:", total)
# print(frequencies["load"] / total)


# Calculate frequency of a word in English langauge corpus


import numpy as np


def cosine_similarity(vector1, vector2):
    # Calculate the dot product of the two vectors
    dot_product = np.dot(vector1, vector2)

    # Calculate the norm (magnitude) of each vector
    norm1 = np.linalg.norm(vector1)
    norm2 = np.linalg.norm(vector2)

    # Calculate cosine similarity
    if norm1 > 0 and norm2 > 0:
        similarity = dot_product / (norm1 * norm2)
    else:
        similarity = 0  # This handles cases where one vector might be all zeros

    return similarity


def calculate_sample_frequency():
    import nltk
    from nltk.corpus import brown
    from nltk.probability import FreqDist

    nltk.download("brown")

    # Load the corpus
    words = brown.words()

    # Calculate frequency distribution
    fdist = FreqDist(words)

    # Get total number of words
    total_words = len(words)

    # Frequency of a specific word, e.g., 'freedom'
    word_frequency = fdist["load"]

    print(word_frequency)
    print(total_words)

    # Probability of picking 'freedom'
    probability = word_frequency / total_words
    print(f"The probability of choosing 'load' is {probability}")


# --------------------------------------------------------------------------------------

import numpy as np
from collections import defaultdict, Counter


def build_cooccurrence_matrix(corpus, window_size=1):
    # Map each word to a unique index
    vocab = list(set(corpus))
    word_to_index = {word: i for i, word in enumerate(vocab)}

    # Create an empty matrix of size (vocab_size x vocab_size)
    vocab_size = len(vocab)
    cooccurrence_matrix = np.zeros((vocab_size, vocab_size), dtype=int)

    # Build the co-occurrence matrix
    for i in range(len(corpus)):
        # Get the index of the target word
        target_word_index = word_to_index[corpus[i]]

        # Calculate the window boundaries safely
        left_bound = max(i - window_size, 0)
        right_bound = min(i + window_size + 1, len(corpus))

        # Count words around the target word within the window
        window_words = corpus[left_bound:i] + corpus[i + 1 : right_bound]
        word_counts = Counter(window_words)

        for word, count in word_counts.items():
            cooccurrence_matrix[target_word_index][word_to_index[word]] += count

    return vocab, cooccurrence_matrix


if __name__ == "__main__":
    from gensim.models import Word2Vec
    from gensim.models.callbacks import CallbackAny2Vec

    # Define the corpus as a list of lists of words (like sentences)
    corpus = [
        """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus
        vehicula lorem arcu, ut tristique sapien placerat a. Etiam nec finibus
        leo. Donec auctor turpis eget massa cursus auctor. Suspendisse sit amet
        sagittis ligula. Aliquam sagittis dignissim tortor, vel laoreet leo
        faucibus non. Proin sit amet tellus pulvinar, imperdiet ex nec,
        bibendum ex. Maecenas efficitur libero dignissim semper varius. Aliquam
        sit amet risus porta, bibendum dui sed, convallis risus. Sed lacinia
        aliquet neque eu ullamcorper. Aenean venenatis, quam sit amet fringilla
        venenatis, libero magna vehicula erat, eu pretium dolor mi et ipsum.
        Aenean ultricies cursus justo, in rutrum lorem molestie a. In hac
        habitasse platea dictumst. Phasellus malesuada, augue sed consectetur
        interdum, sem odio mattis ante, eu pellentesque turpis tellus nec odio.
        Praesent eu mi nunc.

        Nullam tristique enim vitae facilisis bibendum. Quisque volutpat posuere leo
        quis congue. Cras metus lacus, ultrices id interdum eu, gravida sit amet
        turpis. Mauris consectetur porta ex, a scelerisque sem vestibulum ut. Quisque
        tincidunt nulla cursus auctor tincidunt. Aliquam feugiat sem vel imperdiet
        luctus. Suspendisse id nisl eget erat pulvinar viverra nec nec mauris. Nullam
        interdum non nibh a sodales. Proin eu pulvinar ante, vitae tempus dui. Maecenas
        ac fringilla eros. Maecenas congue, dolor et pretium lobortis, dui libero
        laoreet ligula, non scelerisque urna risus nec tellus. Pellentesque condimentum
        massa elit, quis elementum elit bibendum non.

        Aliquam sed efficitur turpis. Praesent sapien libero, tincidunt quis est
        dictum, consectetur mollis dui. Aenean vestibulum ut magna at venenatis. Duis
        condimentum, massa hendrerit aliquet scelerisque, massa mi iaculis lacus, ac
        mollis sapien lorem nec magna. Maecenas ex purus, faucibus ac rhoncus non,
        luctus eget odio. Donec eget scelerisque tortor. Nullam non lobortis metus.
        Nulla sagittis tellus sit amet tempor commodo. Curabitur sed diam quam. Donec
        sed bibendum leo. Morbi eget ex hendrerit, pulvinar leo ut, commodo libero.
        Nunc fermentum interdum mi sit amet pellentesque. Nulla consectetur molestie
        dui et pretium. Vivamus eget ex orci. Cras iaculis tincidunt ornare. Cras sed
        luctus ipsum.

        Praesent eu tempor dui. Nullam sagittis vel nisi dignissim euismod. Nam sit
        amet arcu aliquet, tempus nibh non, hendrerit urna. Nulla facilisi.
        Pellentesque vel ante vitae neque luctus feugiat vel nec mauris. Donec a
        vehicula velit, vel blandit metus. Praesent congue mattis quam non tincidunt.
        Duis eros turpis, efficitur in gravida quis, convallis a est. Nullam eu
        scelerisque mauris, ac tincidunt arcu. Praesent nec lorem a ipsum interdum
        porttitor.

        Proin mattis ullamcorper orci non suscipit. Donec vel laoreet turpis. Mauris
        tempor urna odio, quis dictum felis efficitur eget. Mauris lobortis ipsum vel
        metus malesuada, et ornare massa efficitur. Aliquam euismod accumsan ante.
        Nulla finibus diam ex, quis ornare metus pharetra vitae. Vestibulum laoreet
        eros venenatis nunc tempus porttitor. Donec posuere, dolor posuere cursus
        pulvinar, elit nulla luctus dui, sit amet vestibulum augue ipsum vulputate
        nisl. Suspendisse gravida neque quam, in vehicula justo efficitur sed.
        """.split()
    ]

    # Train a Word2Vec model just to utilize its internal word count and indexing
    model = Word2Vec(
        corpus, window=5, min_count=1, sg=1, workers=1, callbacks=[CallbackAny2Vec()]
    )

    # Create an empty co-occurrence matrix
    import numpy as np

    vocab_size = len(model.wv.key_to_index)
    cooccurrence_matrix = np.zeros((vocab_size, vocab_size), dtype=np.int32)

    # Populate the matrix using the window size from the Word2Vec model
    window_size = model.window
    for sentence in corpus:
        for pos, word in enumerate(sentence):
            word_idx = model.wv.key_to_index[word]
            for i in range(
                max(pos - window_size, 0), min(pos + window_size + 1, len(sentence))
            ):
                if pos != i:  # Do not count the word itself
                    context_word_idx = model.wv.key_to_index[sentence[i]]
                    cooccurrence_matrix[word_idx][context_word_idx] += 1

    vocab = list(model.wv.key_to_index.keys())

    index_word1 = vocab.index("et")  # Replace 'word1' with the actual word
    index_word2 = vocab.index("ornare")  # Replace 'word2' with the actual word
    vector1 = cooccurrence_matrix[index_word1]
    vector2 = cooccurrence_matrix[index_word2]
    similarity = cosine_similarity(vector1, vector2)
    print("Cosine Similarity:", similarity)
