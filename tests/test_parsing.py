from scripts.parsing.parsers import *
from tree_sitter import Language, Parser


def test_clojure():
    parser = Parser()
    parser.set_language(Language("build/parser_bindings.so", "clojure"))
    names = extract(parser, "tests/samples/clojure.clj", extract_clojure)

    assert names["add#1"] == ["add", "a", "b", "+", "a", "b"]
    assert names["add#2"] == ["add", "fn", "a", "b", "+", "a", "b"]
    assert names["private-add#3"] == ["private-add", "a", "b", "+", "a", "b"]
    assert names["square#4"] == ["square", "x", "*", "x", "x"]
    assert names["shape-area#5"] == [
        "shape-area",
        "radius",
        "*",
        "Math",
        "PI",
        "*",
        "radius",
        "radius",
    ]


def test_haskell():
    parser = Parser()
    parser.set_language(Language("build/parser_bindings.so", "haskell"))
    names = extract(parser, "tests/samples/haskell.hs", extract_haskell)

    assert names == {
        "add#1": ["add", "y", "y"],
        "add#2": ["add", "x", "y", "x", "y"],
        "max'#3": ["max'", "x", "y", "x", "y", "x", "otherwise", "y"],
        "add#4": ["add", "x", "y", "x", "y"],
        "square#5": ["square"],
        "factorial#6": [
            "factorial",
            "n",
            "fact",
            "fact",
            "m",
            "m",
            "fact",
            "m",
            "fact",
            "n",
        ],
        "factorial#7": [
            "factorial",
            "n",
            "fact",
            "n",
            "fact",
            "fact",
            "m",
            "m",
            "fact",
            "m",
        ],
        "sumList#8": ["sumList", "foldr"],
        "getInputAndPrint#9": [
            "getInputAndPrint",
            "input",
            "getLine",
            "putStrLn",
            "input",
        ],
    }


def test_elixir():
    parser = Parser()
    parser.set_language(Language("build/parser_bindings.so", "elixir"))
    names = extract(parser, "tests/samples/elixir.ex", extract_elixir)

    assert names == {
        "foo#1": ["foo", "arg1", "arg2", "arg1", "arg2"],
        "bar#2": ["bar", "arg1", "arg2", "arg1", "arg2"],
        "func#3": ["func", "x", "is_number", "x", "add", "x"],
        "func#4": ["func", "x", "is_list", "x", "x"],
        "func#5": ["func", "a", "a"],
        "func#6": ["func", "a", "b", "a", "b"],
    }


def test_erlang():
    parser = Parser()
    parser.set_language(Language("build/parser_bindings.so", "erlang"))
    names = extract(parser, "tests/samples/erlang.erl", extract_erlang)
    assert names == {
        "public_function#1": ["public_function", "Arg", "private_function", "Arg"],
        "private_function#2": ["private_function", "Arg"],
        "anonymous_function_demo#3": [
            "anonymous_function_demo",
            "Add",
            "A",
            "B",
            "A",
            "B",
            "Result",
            "Add",
            "Result",
        ],
        "func#4": ["func", "X", "is_number", "X", "X"],
        "func#5": ["func", "X", "is_list", "X", "length", "X"],
        "func#6": ["func", "A", "A"],
        "func#7": ["func", "A", "B", "A", "B"],
        "recursive_function#8": ["recursive_function", "done"],
        "recursive_function#9": [
            "recursive_function",
            "N",
            "N",
            "recursive_function",
            "N",
        ],
        "init#10": ["init", "Args", "ok", "Args"],
        "handle_call#11": [
            "handle_call",
            "Request",
            "_From",
            "State",
            "reply",
            "ok",
            "State",
        ],
        "handle_cast#12": ["handle_cast", "Msg", "State", "noreply", "State"],
        "say_hello#13": ["say_hello", "SAY_HELLO"],
        "higher_order_function_demo#14": [
            "higher_order_function_demo",
            "HigherOrder",
            "Func",
            "Arg",
            "Func",
            "Arg",
            "Add",
            "A",
            "A",
            "HigherOrder",
            "Add",
        ],
    }


def test_c():
    parser = Parser()
    parser.set_language(Language("build/parser_bindings.so", "c"))
    names = extract(parser, "tests/samples/c.c", extract_c)

    assert names == {
        "add": ["add", "a", "b", "a", "b"],
        "sayHello": ["sayHello", "printf"],
        "getRandomNumber": ["getRandomNumber", "rand"],
        "logTime": ["logTime"],
        "getArray": ["getArray", "arr", "arr"],
        "updateValue": ["updateValue", "value", "value"],
        "average": [
            "average",
            "count",
            "ap",
            "j",
            "sum",
            "va_start",
            "ap",
            "count",
            "j",
            "j",
            "count",
            "j",
            "sum",
            "va_arg",
            "ap",
            "double",
            "va_end",
            "ap",
            "sum",
            "count",
        ],
        "sumOfElements": [
            "sumOfElements",
            "arr",
            "size",
            "sum",
            "i",
            "i",
            "size",
            "i",
            "sum",
            "arr",
            "i",
            "sum",
        ],
        "max": ["max", "a", "b", "a", "b", "a", "b"],
        "multiply": ["multiply", "a", "b", "a", "b"],
        "internalFunction": ["internalFunction", "a", "a", "a"],
        "main": ["main"],
    }


def test_javascript():
    parser = Parser()
    parser.set_language(Language("build/parser_bindings.so", "javascript"))
    names = extract(parser, "tests/samples/javascript.js", extract_javascript)

    assert names == {
        "generateSequence#1": [
            "generateSequence",
            "a",
            "nestedFunction",
            "b",
            "b",
            "greetArrowMultiple",
            "greeting",
            "name",
            "greeting",
            "name",
        ]
    }


def test_python():
    parser = Parser()
    parser.set_language(Language("build/parser_bindings.so", "python"))
    names = extract(parser, "tests/samples/python.py", extract_python)

    assert names == {
        "add#1": ["add", "x", "y", "x", "y"],
        "greet#2": ["greet", "name", "greeting", "greeting", "name"],
        "sum_all#3": ["sum_all", "args", "sum", "args"],
        "describe#4": [
            "describe",
            "kwargs",
            "join",
            "key",
            "value",
            "key",
            "value",
            "kwargs",
            "items",
        ],
        "factorial#5": ["factorial", "n", "n", "n", "factorial", "n"],
        "fib#6": [
            "fib",
            "n",
            "a",
            "b",
            "_",
            "range",
            "n",
            "a",
            "a",
            "b",
            "b",
            "a",
            "b",
        ],
        "instance_method#7": [
            "instance_method",
            "self",
            "value",
            "self",
            "value",
            "value",
        ],
        "class_method#8": ["class_method", "cls", "cls"],
        "static_method#9": ["static_method", "a", "a"],
        "type_hinted_function#10": ["type_hinted_function", "a", "b", "a", "b"],
        "decorator#11": ["decorator", "func", "wrapper"],
        "wrapper#12": ["wrapper", "print", "func", "print"],
        "say_hello#13": ["say_hello", "print"],
    }


def test_java():
    parser = Parser()
    parser.set_language(Language("build/parser_bindings.so", "java"))
    names = extract(parser, "tests/samples/java.java", extract_java)

    assert names == {
        "add#1": ["add", "x", "y", "x", "y"],
        "multiply#2": ["multiply", "x", "y", "x", "y"],
        "sum#3": ["sum", "numbers", "total", "num", "numbers", "total", "num", "total"],
        "add#4": [
            "add",
            "x",
            "y",
            "lambdaRunnable",
            "System",
            "out",
            "println",
            "x",
            "y",
        ],
        "factorial#5": ["factorial", "n", "n", "n", "factorial", "n"],
        "printArray#6": [
            "printArray",
            "array",
            "element",
            "array",
            "System",
            "out",
            "println",
            "element",
        ],
        "run#7": ["Override", "run", "System", "out", "println"],
        "riskyMethod#8": ["riskyMethod"],
        "synchronizedMethod#9": ["synchronizedMethod"],
    }


def test_fortran():
    parser = Parser()
    parser.set_language(Language("build/parser_bindings.so", "fortran"))
    names = extract(parser, "tests/samples/fortran.f90", extract_fortran)

    assert names == {
        "add#1": ["add", "x", "y", "sum", "x", "y", "sum", "sum", "x", "y"],
        "printMessage#2": ["printMessage", "message", "len", "message", "message"],
        "multiply#3": [
            "multiply",
            "x",
            "y",
            "x",
            "y",
            "multiply",
            "x",
            "y",
            "printMessage",
        ],
        "factorial#4": [
            "factorial",
            "n",
            "fact",
            "n",
            "fact",
            "n",
            "fact",
            "fact",
            "n",
            "factorial",
            "n",
        ],
        "average#5": ["average", "x", "y", "x", "y", "average", "x", "y"],
    }


def test_ocaml():
    parser = Parser()
    parser.set_language(Language("build/parser_bindings.so", "ocaml"))
    names = extract(parser, "tests/samples/ocaml.ml", extract_ocaml)
    assert names == {
        "add": ["add", "x", "y"],
        "subtract": ["subtract", "neg", "y", "x", "neg", "y"],
        "multiply": [
            "multiply",
            "inner_multiply",
            "m",
            "n",
            "inner_multiply",
            "x",
            "y",
        ],
        "factorial": ["factorial", "n", "n", "factorial", "n"],
        "abs": ["abs", "x", "x", "x"],
        "pow": ["pow", "exp", "base", "pow", "exp"],
        "gcd": ["gcd", "a", "b", "gcd", "b", "a", "a"],
    }
