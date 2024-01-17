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
pytest tests/test_parsing.py -k test_<language>
```
