import os
import sys
from gensim.models import Word2Vec
from gensim.models.callbacks import CallbackAny2Vec
import logging
import nltk

nltk.download('punkt')

# Configure logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class EpochLogger(CallbackAny2Vec):
    '''Callback to log information about training'''

    def __init__(self):
        self.epoch = 0

    def on_epoch_begin(self, model):
        logging.info(f'Starting epoch {self.epoch}')

    def on_epoch_end(self, model):
        logging.info(f'Finished epoch {self.epoch}')
        self.epoch += 1

def read_corpus(file_list):
    for file_path in file_list:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                yield nltk.word_tokenize(line.lower())

def main(file_list, output_file):
    # Read corpus from files
    corpus = list(read_corpus(file_list))

    # Train Word2Vec model
    model = Word2Vec(corpus, window=5, min_count=1, sg=1, workers=1, callbacks=[EpochLogger()])

    # Save the model to file
    model.save(output_file)
    logging.info(f'Model saved to {output_file}')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <output_model_file> <file1> <file2> ... <fileN>")
        sys.exit(1)

    output_model_file = sys.argv[1]
    input_files = sys.argv[2:]

    main(input_files, output_model_file)
