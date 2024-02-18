## Scripts

### Parsing

#### Downloading tree-sitter parsers

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

### Tests

To run all tests, simply type `pytest`. To run specific language, use:

```
poetry shell
pytest tests/test_parsing.py -k test_<language>
```

### Using parsers from CLI

To run function/name parser for specific file and language:

```
poetry shell
python parsing/print.py -i tests/samples/python.py -l python
```

To print raw AST use option `--ast`:

```
python parsing/print.py -i tests/samples/python.py -l python --ast
```
