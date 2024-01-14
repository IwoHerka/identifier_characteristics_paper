from parsing.parsers import *
from tree_sitter import Language, Parser


def test_clojure():
    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', 'clojure'))
    names = extract(parser, 'tests/samples/clojure.clj', extract_clojure)

    assert names['add#1'] == ['add', 'a', 'b', '+', 'a', 'b']
    assert names['add#2'] == ['add', 'fn', 'a', 'b', '+', 'a', 'b']
    assert names['private-add#3'] == ['private-add', 'a', 'b', '+', 'a', 'b']
    assert names['square#4'] == ['square', 'x', '*', 'x', 'x']
    assert names['shape-area#5'] == ['shape-area', 'radius', '*', 'Math', 'PI', '*', 'radius', 'radius']


def test_haskell():
    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', 'haskell'))
    names = extract(parser, 'tests/samples/haskell.hs', extract_haskell)

    assert names['add#1'] == ['add', 'y', 'y']
    assert names['add#2'] == ['add', 'x', 'y', 'x', 'y']
    assert names["max'#3"] == ["max'", 'x', 'y', 'x', 'y', 'x', 'otherwise', 'y']
    assert names['add#4'] == ['add', 'x', 'y', 'x', 'y']
    assert names['square#5'] == ['square']
    assert names['factorial#6'] == ['factorial', 'n', 'fact', 'n']
    assert names['fact#7'] == ['fact']
    assert names['fact#8'] == ['fact', 'm', 'm', 'fact', 'm']
    assert names['factorial#9'] == ['factorial', 'n', 'fact', 'n']
    assert names['fact#10'] == ['fact']
    assert names['fact#11'] == ['fact', 'm', 'm', 'fact', 'm']
    assert names['sumList#12'] == ['sumList', 'foldr']
    assert names['getInputAndPrint#13'] == ['getInputAndPrint', 'input', 'getLine', 'putStrLn', 'input']


def test_elixir():
    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', 'elixir'))
    names = extract(parser, 'tests/samples/elixir.ex', extract_elixir)
    assert names['foo#1'] == ['foo', 'a', 'b', 'c', 'a', 'b', 'c']
    # TODO


def test_erlang():
    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', 'erlang'))
    names = extract(parser, 'tests/samples/erlang.erl', extract_erlang)
    # TODO


def test_javascript():
    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', 'javascript'))
    names = extract(parser, 'tests/samples/javascript.js', extract_javascript)

    assert names['greet#1'] == ['greet']
    assert names['greetAnon#2'] == ['greetAnon']
    assert names['greetNamed#3'] == ['greetNamed']
    assert names['greetArrow#4'] == ['greetArrow']
    assert names['greetArrowOne#5'] == ['greetArrowOne', 'name']
    assert names['greetArrowMultiple#6'] == ['greetArrowMultiple']
    assert names['greeter#7'] == ['greeter']
    assert names['generateSequence#8'] == ['generateSequence']
    assert names['fetchData#9'] == ['fetchData']


def test_c():
    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', 'c'))
    names = extract(parser, 'tests/samples/c.c', extract_c)

    # TODO
    # assert names


def test_python():
    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', 'python'))
    names = extract(parser, 'tests/samples/python.py', extract_python)


def test_java():
    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', 'java'))
    names = extract(parser, 'tests/samples/java.java', extract_java)


def test_fortran():
    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', 'fortran'))
    names = extract(parser, 'tests/samples/fortran.', extract_fortran)


def test_agda():
    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', 'agda'))
    names = extract(parser, 'tests/samples/agda.', extract_agda)
