import os
import random
import re
from itertools import combinations
from statistics import median

import requests
from rich.console import Console

from db.models import Repo
from db.utils import (
    get_functions,
    init_local_session,
    init_session,
    update_function_metrics,
)

console = Console()

LLM_MODEL = "llama3.2"
LLM_MODEL = "gemma2:9b"
LLM_MODEL = "deepseek-coder-v2:16b"


def rate_relatedness():
    init_session()

    for function in get_functions():
        names = function.names.split(" ")
        pairs = list(combinations(set(names), 2))
        scores = []

        for name1, name2 in pairs:
            prompt = f"""
            Rate how related are two identifiers '{name1}' and '{name2}' from 1 to 5. Only reply with: I score it as <score>
            """

            url = "http://localhost:11434/api/generate"
            payload = {"model": LLM_MODEL, "prompt": prompt, "stream": False}
            response = requests.post(url, json=payload)

            if response.status_code == 200:
                try:
                    json = response.json()["response"]
                    console.print(json)
                    classified_type = json.split("I score it as")[1].strip()

                    for typ in ["1", "2", "3", "4", "5"]:
                        if typ in classified_type:
                            console.print(f"Classified {name1} and {name2} as {typ}")
                            scores.append(int(typ))
                            break
                except:
                    console.print(f"Failed to parse response LLM: {json}")
            else:
                console.print(f"Request failed with status code {response.status_code}")

        console.print(f"Median score for {function.name} is {median(scores)}")
        # update_function_metrics(function, 'relatedness', median(scores))


def classify_all_repos(only_retry=False):
    session = init_local_session()
    repos = Repo.all(session)
    random.shuffle(repos)

    for repo in repos:
        console.print(repo.name)
        if repo.readme is None:
            continue

        if only_retry:
            continue

        if repo.type == repo.type.upper():
          continue

        types = repo.type.split(' ')
        if len(types) != 4:
            continue

        # if repo.type is not None:
        #     types = repo.type.split(' ')
        #     if len(types) > 1 and all(t == types[0] for t in types):
        #         console.print(f"All types are the same for {repo.name}: {types[0]}")
        #         repo.type = types[0].upper()

        typ = classify_repo(repo, session)

        if repo.type is not None:
          repo.type = ' '.join([repo.type, typ])
        else:
          repo.type = typ

        session.commit()

    session.close()


def classify_repo(repo, session):
    prompt = f"""
    Classify open source project "{repo.name}" written in {repo.lang} language into one of the following categories:

    - web - library related to web development or web networking
    - cli - library related to command line, such as CLI utilities, pretty printing, tools for building CLI apps
    - db - library related to databases, such as database ORMs, utilities, integrations and so on
    - ml - project related to machine learning, AI, deep learning, and so on
    - build - project is build tool, such as build system, package manager, etc
    - other - project doesn't fit into any of the above categories

    You can use a fragment of the README file to help you classify the project:
    {repo.readme}

    Don't explain your reasoning, just respond with following format: I classify this project as <type>
    """

    url = "http://localhost:11434/api/generate"
    payload = {"model": LLM_MODEL, "prompt": prompt, "stream": False}
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        try:
            json = response.json()["response"]
            console.print(json)
            classified_type = json.split("I classify this project as")[1].strip()

            for typ in ["web", "cli", "db", "ml", "build", "other"]:
                console.print(f"Checking if {typ} in {classified_type}")
                if typ in classified_type:
                    console.print(f"Classified {repo.name} as {typ}")
                    return typ

            return 'unknown'
        except:
            console.print(f"Failed to parse response LLM: {json}")
            return 'unknown'
    else:
        console.print(f"Request failed with status code {response.status_code}")
        return 'unknown'