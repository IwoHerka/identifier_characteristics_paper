from typing import List, Set, Tuple


def get_conciseness_and_consistency(identifiers):
    consistency_violations = []
    conciseness_violations = []

    for i, id1_soft_words in enumerate(identifiers):
        for j, id2_soft_words in enumerate(identifiers):
            if i != j:
                # Check for consistency violations
                if (
                    id1_soft_words == id2_soft_words[: len(id1_soft_words)]
                    or id1_soft_words == id2_soft_words[-len(id1_soft_words) :]
                ):
                    consistency_violations.append((identifiers[i], identifiers[j]))

                # Check for conciseness violations
                if len(id1_soft_words) < len(id2_soft_words) and " ".join(
                    id1_soft_words
                ) in " ".join(id2_soft_words):
                    conciseness_violations.append(identifiers[i])
                    break  # No need to find more than one violation for conciseness

    return len(consistency_violations), len(conciseness_violations)
