import os
import fasttext

from collections import defaultdict
from db.utils import *
from db.engine import get_engine


def train_fasttext(training_path, output_path):
    """
    Build a list of texts, one per project, save it to temporary training file
    and train fasttext model on it.
    """
    init_session()

    # Prepare training file
    with open(training_path, 'w', encoding='utf-8') as file:
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
