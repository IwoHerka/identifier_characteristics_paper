"""
From Physical and Conceptual Identifier Dispersion: Measures and Relation to Fault Proneness
by Arnaoudova et al.:

To calculate term entropy and context coverage, we extract identifiers found in
class attributes and methods (e.g., names of variables and methods, method
parameters). We split identifiers using a Camel-case splitter to build the term
dictionary (e.g., getText is split into get and text). We filter terms whose
length is less than two characters and summarize the linguistic information in a
term-by-entity matrix. The generic entry a_(i,j) of the term-by-entity matrix
denotes the number of occurrences of the i th term in the j th entity.

Entropy of a discrete random variable measures the amount of uncertainty [23].
To compute the term entropy, we consider terms as random variables with some
associated probability distributions. Given a term, its entries in the
term-by-entity matrix are the counts of term occurrences and thus by normalizing
over the sum of its row entries a probability distribution for each term is
obtained. A normalized entry a_(i,j) is then the probability of the presence of
the term t_i in the j th entity. We then compute term entropy as:

H(t_i) = - sum_(j) a_(i,j) * log(a_(i,j))

With term entropy, the more scattered among entities a term
is, the closer to the uniform distribution is its mass probability
and, thus, the higher is its entropy. On the contrary, if a term
has a high probability to appear in few entities, then its entropy
value will be low.

Based on this, describe how to adapt this general approach to calculate now
scattered identifiers are across functions, files and different repos. So,
instead of term entropy, I want identifier entropy. Assume I have a relational
database which contains repos table with lang colum, function table with
columns: name, names (all names inside its body), repo_id and unique file
path/name. You can also assume you can use python scripts based on sqlalchemy to
query the data and do calculations. Only results should be saved to the
database.
"""

import math
from statistics import median
from collections import defaultdict
from rich.console import Console

from db.utils import get_functions_for_repo, get_repos, update_function_metrics

console = Console()


def calculate_term_entropy(normalize=False):
    """
    Given a repo_id, calculate term entropy where term is identifier and entity
    is function.  In other words, how scattered identifiers are across functions
    with in a repo. Results are optionally normalized by maximum entropy score
    in the repo.

    The entropy measures the unpredictability or dispersion of the occurrences
    of the identifier across the functions. A higher entropy value indicates
    that the identifier appears more uniformly across multiple functions, while
    a lower value suggests that it is concentrated in fewer functions.

    The normalization divides the entropy by the maximum entropy score
    in the dataset, allowing for comparison relative to the highest entropy
    score found among all identifiers.

    Example:

    If there are 10 functions in a repository, the normalized entropy score of
    0.3 for "foo" suggests that its distribution among those functions is less
    uniform than other identifiers with higher scores but does not equate to the
    number of functions it appears in.  If "foo" appeared in 3 out of the 10
    functions, its entropy score would depend on how frequently it appeared in
    those functions compared to its total appearances in all functions.

    If "foo" appears in 2 functions, A (2 occurrences), B (1 occurrence) then:
    
        H(foo) = - (2/3 * log(2/3) + 1/3 * log(1/3))= 0.9183
    """
    for repo in get_repos():
        console.print(f"Calculating term entropy for repo {repo.id}")
        functions = get_functions_for_repo(repo.id)

        # Step 1: Build identifier occurrence matrix
        identifier_entity_matrix = defaultdict(lambda: defaultdict(int))
        
        # Step 2: Populate the matrix with identifier occurrences in functions
        for function in functions:
            identifiers = function.names.split() 

            for identifier in identifiers:
                identifier_entity_matrix[identifier][function.id] += 1

        # Step 3: Calculate entropy for each identifier
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

        # Step 4: Normalize entropy values to the range [0, 1] by max entropy
        if normalize and identifier_entropy_results:
            max_entropy = max(entropy for _, entropy in identifier_entropy_results)

            # TODO: Fix normalize            
            # identifier_entropy_results = [
            #     (identifier, entropy / max_entropy) if max_entropy > 0 else (identifier, 0)
            #     for identifier, entropy in identifier_entropy_results
            # ]

        for function in functions:
            names = function.names.split()

            entropies = []
            for name in names:
                entropies.append(identifier_entropy_results[name])

            update_function_metrics(function, "median_term_entropy", median(entropies))
            console.print(f"Median term entropy for {function.name}: {median(entropies)}")
