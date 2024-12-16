## Concreteness value of a unigram word

The concreteness value of a unigram word w, denoted as fc(w), is determined as
follows:

- If w is a word in the concreteness dictionary, its concreteness value is
  retrieved from the dictionary. For example, the concreteness value of “old” is
  2.72.
- If w is an abbreviation, the concreteness rating is the same as that of the
  original word. For example, “src” is an abbreviation of “source”. The
  concreteness value of “source”, i.e., 1.48, is used for the abbreviation. We
  have extracted 62 million abbreviations from 419 million variable names from
  Github.com using BOA framework and Segmentation package [6]. The completed
  abbreviation list can be accessed at to allow for verification and
  replication.
- If w has a pre-suffix or post-suffix, its concreteness value is the same as
  its original form. For example, the original form of “Loader” is “load”.
- If w does not belong to the above cases, its concreteness value is zero.
- Justify the concreteness value based on the unigram usages difference between
  in programming and English language. The justification factor is the unigram
  frequency distribution ratio between the unigram dictionary we have
  extracted from Github repository and English dictionary. For example, the
  justification factor for the unigram “load” is 0.0035/0.000065=55.

## Concreteness value of a multigram word

Concreteness value of a multigram: The concreteness value of a multigram is
calculated based on word similarity among the unigrams of which the multigram is
composed. There are mainly two kinds of word similarity, i.e., conceptual
similarity and relational similarity, as studied in the area of natural language
processing.

TODO: compute similarity for a project and global (NLTK)

Based on word similarity, we determine the concreteness rating of a multigram in
two steps:

- Determining the dominant unigram concreteness (duc) for a given multigram. The
  duc value is defined as the maximum concreteness value of all unigrams of which
  a multigram consists. For a bigram composed of words w1 and w2, duc(w1,w2)
  =max(fc(w1), fc(w2)). For example, duc(class, load)=max(3.86, 3.36) =3.86.

- Determining the concreteness gaining rates (Δcgr). It measures the extra
  concreteness gained in percentage when the additional unigram used for variable
  names. The evaluation of Δcgr is based on the assumption that the additional
  unigram is needed for naming a variable because it refines the meaning of the
  previous unigrams. For example, “classLoader” is more informative than “loader”
  or “class” because “classLoader” specifies the type of the “loader”, and
  therefore increases the concreteness value. We have two observations: (a) the
  degree of the relational similarity between two words is positively correlated
  with Δcgr. Intuitively, people intentionally or unintentional to arrange two
  words' cooccurrences to help themselves comprehend the meaning of sentences
  accurately. For example, rSim(news, article) is higher than rSim(class, load)
  because the probability of co-occurrence (news, article) is greater than (class,
  load). (b) The degree of conceptual similarity between two words is negatively
  correlated with Δcgr. It is meaningless for developers to name a multigram
  variable using two synonyms. However, the dissimilarity of a conceptual
  similarity is positively correlated with Δcgr.

## Definitions

### 1. Dominant unigram concreteness

The dominant unigram concreteness value $duc$ for a given multigram is defined as
follows:

```math
duc(multigram) = ܿmax_n(fc(w_i))
```

where $n$ is the size of the multigram and $w_i$ is the ith unigram of the multigram.

### 2. Dissimilarity of conceptual similarity

The dissimilarity of conceptual similarity $disCSim$ between $w_1$ and $w_2$ is defined as follows:

```math
disCSim(w_1, w_2) = 1 - cSim(w_1, w_2)
```

### 3. Concreteness value gain

The concreteness value gain Δcgr is defined as follows:

```math
Δcgr(multigram) = sum_{ij}(rSim(w_i, w_j) * disCSim(w_i, w_j))
```

### 4. Concreteness of a variable name

```math
Concreteness(v) =
\begin{cases}
fc(v), & \text{if } v \text{ is a unigram} \\
duc(v) \cdot (1 + \Delta cgr(v)), & \text{if } v \text{ is a multigram}
\end{cases}
```
