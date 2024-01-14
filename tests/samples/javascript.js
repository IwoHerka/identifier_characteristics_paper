// Function Declaration
function greet() {
    return "Hello, world!";
}

// Anonymous Function Expression
const greetAnon = function() {
    return "Hello, world!";
};

// Named Function Expression
const greetNamed = function greetFunction() {
    return "Hello, world!";
};

// Arrow Function
// Without parameters
const greetArrow = () => "Hello, world!";
// With one parameter
const greetArrowOne = name => "Hello, " + name + "!";
// With multiple parameters
const greetArrowMultiple = (greeting, name) => greeting + ", " + name + "!";

// Shorthand Method Definition in Object Literal
const greeter = {
    greet() {
        return "Hello, world!";
    }
};

// Generator Function
function* generateSequence() {
    yield 1;
    yield 2;
    return 3;
}

// Async Function
async function fetchData() {
    const data = await fetch('https://api.example.com');
    return data.json();
}
