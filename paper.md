# Abstract

_Identifier names convey useful information about the intended semantics of
code. Name-based program analyses leverage this information to detect bugs,
predict types, and enhance code readability._ Although numerous lexicon metrics
have been introduced, there remains a lack of comprehensive tools that integrate
these metrics to provide a holistic analysis of identifier characteristics and
their impact on software quality. To address this challenge, we have developed a
framework named NameBench, designed to automate large-scale identifier analysis
across many programming languages and paradigms. The framework is customizable
and extensible, allowing for the support of new metrics, languages, and
experiment configurations. It systematically integrates a comprehensive suite of
identifier characteristics and metrics. These include basic ones, such as
identifier length, the count of unique and duplicate identifiers, the prevalence
of short identifiers, casing styles, abbreviation usage, dictionary word
incorporation, and others, as well as more complex ones, such as Levenshtein
distance, term entropy, violations of conciseness and consistency, context
coverage, semantic similarity, external similarity, grammatical patterns, and
word concreteness. To help with large-scale project analysis, the framework also
employs large language models to automatically categorize projects according to
their domain. To test the framework, we performed a small pilot study, which
included 1000 projects from the GitHub dataset, across 10 programming languages,
3 programming paradigms, and 3 project domains.

# Introduction

a) RQ1: Do common identifier characteristics reproduce across programming paradigms?

b) RQ2: Do common identifier characteristics reproduce across project domains?

c) RQ3: Do grammatical patterns found in procedural paradigms reproduce in
functional paradigms?

d) RQ4: Can LLMs be used as ground truth for relatedness of identifiers?

e) RQ5: Can word embedding models be trained only on identifier names instead of AST?

f) RQ6: To what extent can large language models help domain categorization for software repositories?
