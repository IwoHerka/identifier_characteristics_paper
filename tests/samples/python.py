# 1. Basic Function Definition
def add(x, y):
    return x + y


# 2. Function with Default Arguments
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"


# 3. Function with Variable Number of Arguments
def sum_all(*args):
    return sum(args)


# 4. Function with Keyword Arguments
def describe(**kwargs):
    return ", ".join(f"{key}={value}" for key, value in kwargs.items())


# 5. Anonymous (Lambda) Function
multiply = lambda x, y: x * y


# 6. Recursive Function
def factorial(n):
    if n == 1:
        return 1
    return n * factorial(n - 1)


# 7. Generator Function (using yield)
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b


# 8. Method (Function within a Class)
class MyClass:
    def instance_method(self, value):
        self.value = value

    @classmethod
    def class_method(cls):
        return cls

    @staticmethod
    def static_method(a):
        return a


# 9. Function with Type Hints (Python 3.5+)
def type_hinted_function(a: int, b: str) -> str:
    return f"{a}: {b}"


# 10. Decorated Function
def decorator(func):
    def wrapper():
        print("Something is happening before the function is called.")
        func()
        print("Something is happening after the function is called.")
    return wrapper


@decorator
def say_hello():
    print("Hello!")

