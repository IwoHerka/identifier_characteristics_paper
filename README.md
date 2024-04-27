## Scripts

Activate Poetry shell with:

```
poetry shell
```

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

### Using parsers from CLI

To run function/name parser for specific file and language:

```
python parsing/print.py -i tests/samples/python.py -l python
```

To print raw AST use option `--ast`:

```
python parsing/print.py -i tests/samples/python.py -l python --ast
```

### Misc. scripts

```bash
# Count number of directories
ls -l data/erlang/ | grep -c ^d
# Delete empty directories
find data/erlang -type d -empty -delete
# Count directories recursively
find data/erlang -type d | wc -l
# Count files by extension recursively
find data/erlang/ -type f | awk -F. '/\./ {print $NF}' | sort | uniq -c | sort -nr
# Remove all files which don't have specified extension
find data/erlang -type f ! -name '*.erl' -exec rm -f -v {} +
# Remove all files which don't have specified extension or are README.md
find data/python -type f ! \( -name '*.py' -o -name 'README.*' \) -exec rm -f -v {} +
```

```
touch build/raw/all.txt
cat build/raw/erlang.txt >> build/raw/all.txt
```

```
shopt -s nocaseglob
find . -type f ! \( \
    -name '*.f' -o \
    -name '*.for' -o \
    -name '*.ftn' -o \
    -name '*.f90' -o \
    -name '*.f95' -o \
    -name '*.f03' -o \
    -name '*.f08' -o \
    -name '*.f15' -o \
    -name '*.f18' -o \
    -name '*.fpp' -o \
    -name 'README.md' \
\) -exec rm {} +
```
