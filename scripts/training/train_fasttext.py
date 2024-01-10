import os

import fasttext
from rich.console import Console

from db.utils import init_session

console = Console()


def train(training_path, output_dir):
    """
    Build a list of texts, one per project, save it to temporary training file
    and train fasttext model on it.
    """
    init_session()

    console.print(f"Training fasttext model with window size 5...")
    model = fasttext.train_unsupervised(
        training_path, "skipgram", minCount=3, lr=0.1, ws=5, epoch=5, dim=100, thread=24
    )
    model.save_model(os.path.join(output_dir, "fasttext_5ws.bin"))

    console.print(f"Training fasttext model with window size 2...")
    model = fasttext.train_unsupervised(
        training_path, "cbow", minCount=3, lr=0.1, ws=2, epoch=5, dim=100, thread=24
    )
    model.save_model(os.path.join(output_dir, "fasttext_2ws.bin"))
