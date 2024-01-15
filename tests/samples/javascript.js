// function declaration
function greet() {
    return "Hello, world!";
}


// anonymous function expression
const greetAnon = function() {
    return "Hello, world!";
};


// named function expression
const greetNamed = function greetFunction() {
    return "Hello, world!";
};

// arrow function
// without parameters
const greetArrow = () => "Hello, world!";


// with one parameter
const greetArrowOne = name => "Hello, " + name + "!";


// with multiple parameters
const greetArrowMultiple = (greeting, name) => greeting + ", " + name + "!";


// shorthand method definition in object literal
const greeter = {
    greet() {
        return "Hello, world!";
    }
};


// generator function
function* generateSequence() {
    yield 1;
    yield 2;
    return 3;
}


// async function
async function fetchData() {
    const data = await fetch('https://api.example.com');
    return data.json();
}
