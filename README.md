## Scripts

### Parsing

#### Downloading tree-sitter parsers

```
git submodule update --init --force --remote
```

Compile tree-sitter parser (`build/parser_bindings.so`):

```bash
python parsing/compile.py
```

You can test parsing using `parsing/print.py` script. Samples are in `tests/samples/`
directory.

### Tests

To run tests, simply type `pytest`.
