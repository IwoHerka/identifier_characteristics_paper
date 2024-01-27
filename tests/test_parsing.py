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

    assert names['foo#1'] == ['foo', 'arg1', 'arg2', 'arg1', 'arg2']
    assert names['bar#2'] == ['bar', 'arg1', 'arg2', 'arg1', 'arg2']
    assert names['func#3'] == ['func',  'x', 'is_number', 'x', 'x']
    assert names['func#4'] == ['func', 'x', 'is_list', 'x', 'x']
    assert names['func#5'] == ['func', 'a', 'a']
    assert names['func#6'] == ['func', 'a', 'b', 'a', 'b']


def test_erlang():
    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', 'erlang'))
    names = extract(parser, 'tests/samples/erlang.erl', extract_erlang)

    assert names['public_function#1'] == ['public_function', 'Arg', 'private_function', 'Arg']
    assert names['private_function#2'] == ['private_function', 'Arg']
    assert names['anonymous_function_demo#3'] == ['anonymous_function_demo', 'Add', 'A', 'B', 'A', 'B', 'Result', 'Add', 'Result']
    assert names['func#4'] == ['func', 'X', 'is_number', 'X', 'X']
    assert names['func#5'] == ['func', 'X', 'is_list', 'X', 'length', 'X']
    assert names['func#6'] == ['func', 'A', 'A']
    assert names['func#7'] == ['func', 'A', 'B', 'A', 'B']
    assert names['recursive_function#8'] == ['recursive_function', 'done']
    assert names['recursive_function#9'] == ['recursive_function', 'N', 'N', 'recursive_function', 'N']
    assert names['init#10'] == ['init', 'Args', 'ok', 'Args']
    assert names['handle_call#11'] == ['handle_call', 'Request', '_From', 'State', 'reply', 'ok', 'State']
    assert names['handle_cast#12'] == ['handle_cast', 'Msg', 'State', 'noreply', 'State']
    assert names['say_hello#13'] == ['say_hello', 'SAY_HELLO']
    assert names['higher_order_function_demo#14'] == ['higher_order_function_demo', 'HigherOrder', 'Func', 'Arg', 'Func', 'Arg', 'Add', 'A', 'A', 'HigherOrder', 'Add']


def test_c():
    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', 'c'))
    names = extract(parser, 'tests/samples/c.c', extract_c)

    assert names['add#1'] == ['add', 'a', 'b', 'a', 'b']
    assert names['sayHello#2'] == ['sayHello', 'printf']
    assert names['getRandomNumber#3'] == ['getRandomNumber', 'rand']
    assert names['logTime#4'] == ['logTime']
    assert names['getArray#5'] == ['getArray', 'arr', 'arr']
    assert names['updateValue#6'] == ['updateValue', 'value', 'value']
    assert names['average#7'] == ['average', 'count', 'ap', 'j', 'sum', 'va_start', 'ap', 'count', 'j', 'j', 'count', 'j', 'sum', 'va_arg', 'ap', 'double', 'va_end', 'ap', 'sum', 'count']
    assert names['sumOfElements#8'] == ['sumOfElements', 'arr', 'size', 'sum', 'i', 'i', 'size', 'i', 'sum', 'arr', 'i', 'sum']
    assert names['max#9'] == ['max', 'a', 'b', 'a', 'b', 'a', 'b']
    assert names['multiply#10'] == ['multiply', 'a', 'b', 'a', 'b']
    assert names['internalFunction#11'] == ['internalFunction', 'a', 'a', 'a']
    assert names['main#12'] == ['main']


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


def test_python():
    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', 'python'))
    names = extract(parser, 'tests/samples/python.py', extract_python)

    assert names['add#1'] == ['add', 'x', 'y', 'x', 'y']
    assert names['greet#2'] == ['greet', 'name', 'greeting', 'greeting', 'name']
    assert names['sum_all#3'] == ['sum_all', 'args', 'sum', 'args']
    assert names['describe#4'] == ['describe', 'kwargs', 'join', 'key', 'value', 'key', 'value', 'kwargs', 'items']
    assert names['factorial#5'] == ['factorial', 'n', 'n', 'n', 'factorial', 'n']
    assert names['fib#6'] == ['fib', 'n', 'a', 'b', '_', 'range', 'n', 'a', 'a', 'b', 'b', 'a', 'b']
    assert names['instance_method#7'] == ['instance_method', 'self', 'value', 'self', 'value', 'value']
    assert names['class_method#8'] == ['class_method', 'cls', 'cls']
    assert names['static_method#9'] == ['static_method', 'a', 'a']
    assert names['type_hinted_function#10'] == ['type_hinted_function', 'a', 'b', 'a', 'b']
    assert names['decorator#11'] == ['decorator', 'func', 'wrapper']
    assert names['wrapper#12'] == ['wrapper', 'print', 'func', 'print']
    assert names['say_hello#13'] == ['say_hello', 'print']


def test_java():
    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', 'java'))
    names = extract(parser, 'tests/samples/java.java', extract_java)

    assert names['add#1'] == ['add', 'x', 'y', 'x', 'y']
    assert names['multiply#2'] == ['multiply', 'x', 'y', 'x', 'y']
    assert names['sum#3'] == ['sum', 'numbers', 'total', 'num', 'numbers', 'total', 'num', 'total']
    assert names['add#4'] == ['add', 'x', 'y', 'x', 'y']
    assert names['factorial#5'] == ['factorial', 'n', 'n', 'n', 'factorial', 'n']
    assert names['printArray#6'] == ['printArray', 'array', 'element', 'array', 'System', 'out', 'println', 'element']
    assert names['run#7'] == ['Override', 'run', 'System', 'out', 'println']
    assert names['riskyMethod#8'] == ['riskyMethod']
    assert names['synchronizedMethod#9'] == ['synchronizedMethod']


def test_fortran():
    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', 'fortran'))
    names = extract(parser, 'tests/samples/fortran.f90', extract_fortran)

    assert names['add#1'] == ['add', 'x', 'y', 'sum', 'x', 'y', 'sum', 'sum', 'x', 'y']
    assert names['printMessage#2'] == ['printMessage', 'message', 'len', 'message', 'message']
    assert names['multiply#3'] == ['multiply', 'x', 'y', 'x', 'y', 'multiply', 'x', 'y', 'printMessage']
    assert names['factorial#4'] == ['factorial', 'n', 'fact', 'n', 'fact', 'n', 'fact', 'fact', 'n', 'factorial', 'n']
    assert names['average#5'] == ['average', 'x', 'y', 'x', 'y', 'average', 'x', 'y']


def test_ocaml():
    parser = Parser()
    parser.set_language(Language('build/parser_bindings.so', 'ocaml'))
    names = extract(parser, 'tests/samples/ocaml.ml', extract_ocaml)

    assert names['add#1'] == ['add', 'x', 'y']
    assert names['subtract#2'] == ['subtract', 'neg', 'y', 'x', 'neg', 'y']
    assert names['multiply#3'] == ['multiply', 'inner_multiply', 'm', 'n', 'inner_multiply', 'x', 'y']
    assert names['factorial#4'] == ['factorial', 'n', 'n', 'factorial', 'n']
    assert names['abs#5'] == ['abs', 'x', 'x', 'x']
    assert names['pow#6'] == ['pow', 'exp', 'base', 'pow', 'exp']
    assert names['gcd#7'] == ['gcd', 'a', 'b', 'gcd', 'b', 'a', 'a']
