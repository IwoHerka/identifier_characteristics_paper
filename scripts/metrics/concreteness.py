

file = 'build/unigrams.txt'

def load_word_frequencies(file_path):
    # Initialize an empty dictionary to store word frequencies
    word_frequencies = {}
    # Initialize a variable to hold the sum of all occurrences
    total_occurrences = 0
    
    # Open the file at the given path
    with open(file_path, 'r') as file:
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

def calculate_sample_frequency():
    import nltk
    from nltk.corpus import brown
    from nltk.probability import FreqDist

    nltk.download('brown')

    # Load the corpus
    words = brown.words()

    # Calculate frequency distribution
    fdist = FreqDist(words)

    # Get total number of words
    total_words = len(words)

    # Frequency of a specific word, e.g., 'freedom'
    word_frequency = fdist['load']

    print(word_frequency)
    print(total_words)

    # Probability of picking 'freedom'
    probability = word_frequency / total_words
    print(f"The probability of choosing 'load' is {probability}")

