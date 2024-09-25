import os
from gensim.models import Word2Vec
from gensim.models.callbacks import CallbackAny2Vec

from rich.console import Console
from collections import defaultdict
from db.utils import get_lang_to_repo_ids_map, get_ordered_function_names
from db.engine import get_engine


console = Console()


class EpochLogger(CallbackAny2Vec):
    """Callback to log information about training"""

    def __init__(self):
        self.epoch = 0

    def on_epoch_begin(self, model):
        console.print(f"Starting epoch {self.epoch}")

    def on_epoch_end(self, model):
        console.print(f"Finished epoch {self.epoch}")
        self.epoch += 1


def train(output_path):
    corpus = []

    for lang, repos in get_lang_to_repo_ids_map().items():
        for repo_id in repos:
            names = get_ordered_function_names(repo_id)

            if names != "":
                corpus.append(names.strip().split())

    console.print("Starting training...")
    model = Word2Vec(
        corpus, window=5, min_count=1, sg=1, workers=1, callbacks=[EpochLogger()]
    )
    model.save(output_path)
    console.print(f"Done, vocab size: {len(model.wv.key_to_index)}")
