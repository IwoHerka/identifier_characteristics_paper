import math
from collections import defaultdict
from statistics import median

from rich.console import Console

from db.models import Repo
from db.utils import get_functions_for_repo, init_local_session

console = Console()


def calculate_term_entropy():
    session = init_local_session()

    for repo in Repo.all(session, selected=True):
        console.print(f"Calculating term entropy for repo {repo.id}")
        functions = get_functions_for_repo(repo.id, session)

        all_have_term_entropy = all(
            function.term_entropy is not None for function in functions
        )
        if all_have_term_entropy:
            console.print(
                f"All functions in repo {repo.id} already have term_entropy calculated. Skipping..."
            )
            continue

        identifier_entity_matrix = defaultdict(lambda: defaultdict(int))

        for function in functions:
            identifiers = function.names.split()

            for identifier in identifiers:
                identifier_entity_matrix[identifier][function.id] += 1

        identifier_entropy_results = {}

        for identifier, entities in identifier_entity_matrix.items():
            total_count = sum(entities.values())

            if total_count == 0:
                continue

            entropy = 0

            for _, count in entities.items():
                prob = count / total_count

                if prob > 0:  # Avoid log(0)
                    entropy -= prob * math.log(prob)

            identifier_entropy_results[identifier] = entropy

        for function in functions:
            names = function.names.split()

            entropies = []
            for name in names:
                entropies.append(identifier_entropy_results[name])

            if len(entropies) > 0:
                function.term_entropy = median(entropies)
                session.add(function)
                try:
                    console.print(
                        f"Median term entropy for {function.name}: {median(entropies)}"
                    )
                except:
                    pass

        session.commit()
