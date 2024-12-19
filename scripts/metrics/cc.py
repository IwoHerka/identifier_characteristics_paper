from typing import List, Set, Tuple


def get_conciseness_and_consistency(
    identifiers: List[List[str]],
) -> Tuple[Set[Tuple[str, str]], Set[str]]:
    """
    Based on the definition of syntactic synonym consistency and conciseness
    (Syntactic Identifier Conciseness and Consistency, Lawrie et al.):

    Syntactic Synonym Consistency is violated between two identifiers if one
    identifier's sequence of soft words (essentially, the "name" broken down into
    its constituent parts) is fully contained within the other, with additional
    words either at the beginning or the end. Syntactic Conciseness is violated
    for an identifier if there exists another identifier that contains the same
    sequence of soft words plus additional words either at the beginning or the
    end.

    This function:
    - Checks each pair of identifiers for syntactic synonym consistency violations.
    - Checks each identifier against all others for syntactic conciseness violations.
    - Returns sets of identifier pairs that violate consistency and identifiers
      that violate conciseness.
    """
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
