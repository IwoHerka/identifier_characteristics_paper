### Identifier characteristics across programming langauges and project domains: an empirical study

This repository contains scripts and source code used in the paper.

#### Directory structure

- `db/` - Database models and utilities
- `docker/` - Docker configuration for running database
- `nlp/fasttext/` - IdBench benchmark script for fastText model
- `parsers/` - Tree-sitter language persers
- `scripts/extract` - Function and gramamr extraction related code. Grammar extraction requires locally running SCANL tagger
- `scripts/metrics` - Metric calculation scripts
- `scripts/parsing` - Parsing source code
- `scripts/training` - fastText model training script
- `scripts/download` - Repository download code

#### Main script

Main script for the repository is `main.py` which can be used to run most operations.
Some scripts are meant to be run directly with `python <script>`. 
Models, abbreviations, unigram list, concreteness ratings and frequency distribution files should be placed in `build/` directory.
Download scripts require `GITHUB_TOKEN` environment variable.

#### Docker

`start_db.sh` can be run to start local database on port 5444.

#### Parsing

##### Downloading tree-sitter parsers

```
git submodule update --init --force --remote
```

Compile tree-sitter parser:

```bash
python parsing/compile.py
```

This should produce `build/parser_bindings.so` file with bindings for all langauges.
You can test parsing using `parsing/print.py` script. Samples are in `tests/samples/`
directory.

#### Tests

To run all tests, simply type `pytest`. To run specific language, use:

```
pytest tests/test_parsing.py -k test_<language>
```

#### Using parsers from CLI

To run function/name parser for specific file and language:

```
python parsing/print.py -i tests/samples/python.py -l python
```

To print raw AST use option `--ast`:

```
python parsing/print.py -i tests/samples/python.py -l python --ast
```
