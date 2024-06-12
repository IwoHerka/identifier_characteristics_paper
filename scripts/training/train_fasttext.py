import os

import fasttext
from collections import defaultdict

from rich.console import Console

from db.utils import *
from db.engine import get_engine

console = Console()


def train_fasttext(training_path, output_path):
    """
    Build a list of texts, one per project.
    """
    init_session()

    with open(training_path, 'w', encoding='utf-8') as file:
        # TODO: Possibly some limit? Way of selecting projects?
        for lang, repos in get_lang_to_repo_ids_map().items():
            for repo_id in repos:
                names = get_ordered_function_names(repo_id)
    
                file.write(names)
                file.write(' ')

    model = fasttext.train_unsupervised(
        training_path,
        'cbow',
        minCount=3,
        lr=0.1,
        ws=5,
        epoch=5,
        dim=100,
        thread=24
    )

    model.save_model(output_path)
