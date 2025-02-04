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

## Introduction

In programming, identifier names play a crucial role in conveying the intended
semantics of code. They serve as the primary means by which developers
communicate the purpose and functionality of variables, functions, classes, and
other entities within a codebase. Well-chosen names can significantly enhance
code readability, making it easier for developers to understand, maintain, and
collaborate on software projects. Conversely, poorly chosen names can lead to
confusion, misinterpretation, and increased cognitive load, ultimately resulting
in bugs and inefficiencies.

The significance of naming extends beyond mere aesthetics; it has been shown
that meaningful identifiers can improve the overall quality of
software.[citation needed] Research indicates that developers often rely on
identifier names to infer the behavior of code, especially when navigating
unfamiliar codebases [?]. As such, the practice of thoughtful naming is not only
a matter of personal preference but a fundamental aspect of software engineering
that impacts the effectiveness of communication among team members and the
maintainability of the code over time.

Name-based program analyses leverage the information embedded in identifier
names to perform various tasks that enhance software quality. Key applications
include bug detection, type prediction, code readability enhancement,
refactoring support, and documentation generation [?].

Despite the importance of these applications, there remains a lack of
comprehensive tools that integrate various lexicon metrics to provide a holistic
analysis of identifier characteristics across different programming languages
and paradigms. This gap highlights the need for frameworks such as NameBench,
which aim to systematically analyze and enhance the understanding of identifier
semantics in source code repositories.

### Research questions

- RQ1: Do common identifier characteristics correlate with programming paradigms?
- RQ2: Do common identifier characteristics correlate with project domains?
- RQ3: Do common identifier characteristics correlate with programming languages?
- RQ4: Do grammatical patterns found in procedural paradigms reproduce in functional paradigms?
- RQ5: Can LLMs be used as ground truth for relatedness of identifiers?
- RQ6: Can word embedding models be trained only on identifier names instead of AST?
- RQ7: To what extent can large language models help domain categorization for software repositories?

# Related work

- Review all metrics papers
- Review my review

# Methodology

## Data collection

### Repository download

We automate the retrieval of repositories from GitHub by selecting a specified
number of the most popular repositories for each supported programming language,
based on the number of stars they have received using GitHub public API. The
framework gathers repository metadata, including details such as the author,
programming language, and star count. To optimize the download process, we
employ Git's sparse checkout feature, which allows us to selectively clone only
the source code files and README, minimizing unnecessary data transfer.
Repository information is saved in the PostgreSQL database.

### Identifier extraction

After downloading the repositories, the subsequent step involves the extraction
of functions and identifiers from the source code files. This process entails
parsing each file to isolate the functions and identifiers it contains. For each
supported language, a custom extraction function is employed, which parses the
concrete syntax tree generated by the tree-sitter parser generator [?].

We incorporate all possible function forms for each language, including
anonymous functions, which are prevalent in functional languages. For
instance, in Haskell, we account for standard function definitions, those with
guards, pattern matching, as well as monadic and shorthand anonymous
functions. See figure [?].

[Haskell functions figure]

## Data processing

### Repository classification

For repository classification, we employ three large language models: LLama 3.2,
Gemma 2 (9B), and Phi 3 (14B). These models were chosen for their state-of-the-art
performance in natural language understanding and their ability to handle diverse
and complex classification tasks [?]. Each model is tasked with classifying the
repositories which contain README. The responses are parsed, and those that
adhere to the requested response format are retained. In the first round,
repositories that receive consistent classifications from all three models are
deemed classified and subsequently removed from further analysis. In the second
round, the models are queried again, and the classification receiving the
majority of votes (out of six) is adopted for the remaining repositories. LLM
prompt is as follows:

> Classify open source project "{name}" written in {language} language into one of the following categories:
>
> - web - library related to web development or web networking
> - cli - library related to command line, such as CLI utilities, pretty printing, tools for building CLI apps
> - db - library related to databases, such as database ORMs, utilities, integrations and so on
> - ml - project related to machine learning, AI, deep learning, and so on
> - build - project is build tool, such as build system, package manager, etc
> - other - project doesn't fit into any of the above categories
>
>   You can use a fragment of the README file to help you classify the project: {first 20 lines of README}
>
> Don't explain your reasoning, just respond with following format: I classify this project as <type>

### Word embedding model training

### Results

- Discuss each metric with other metrics, lang, project
- pvalues and ANOVA tests
- Graphs and raw numeric results

### Discussion

The results of our study reveal statistically significant differences in various
identifier metrics across different programming languages, paradigms, and
project domains. These differences highlight the nuanced ways in which
identifier naming conventions and characteristics can vary depending on the
context. However, it is important to note that while these differences are
statistically significant, they may not be practically significant for the
average developer. In practice, the variations in identifier metrics are often
too small to have a meaningful impact on day-to-day coding activities or
software maintenance. This suggests that while identifier metrics can provide
valuable insights for large-scale analyses and tool development, individual
developers may not need to prioritize these differences in their routine coding
practices.

The correlations identified in this study are likely attributable to several key factors:

- The size and age of the project
- The number of developers involved
- The problem domain
- The syntax and semantics of the programming language
- The culture of the developers
- The programming paradigm
- The architectural style (e.g., Domain-Driven Design, Hexagonal Architecture, etc.)
- Whether the project is open source or proprietary

These fundamental factors are likely to correlate themselves with language
choice, paradigm, and domain type. Therefore, to gain a more comprehensive
understanding of the determinants of identifier characteristics within a project
(and how those factors are related to each other) a more extensive study
encompassing a significantly larger number of projects is necessary, accounting
for the aforementioned factors.
