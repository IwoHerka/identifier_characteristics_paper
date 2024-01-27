// function declaration
function greet(a) {
    return a + "Hello, world!";
}


// anonymous function expression
const greetAnon = function(a) {
    return "Hello, world!" + a;
};


// named function expression
const greetNamed = function greetFunction(a) {
    return "Hello, world!" + a;
};

// arrow function
// without parameters
const greetArrow = (a) => "Hello, world!" + a;


// with one parameter
const greetArrowOne = name => "Hello, " + name + "!";


// with multiple parameters
const greetArrowMultiple = (greeting, name) => greeting + ", " + name + "!";


// shorthand method definition in object literal
const greeter = {
    greet(a) {
        return "Hello, world!" + a;
    }
};


// generator function
function* generateSequence(a) {
    yield a;
    yield 1;
    yield 2;
    return 3;
}


// // async function
async function fetchData(a) {
    const data = await fetch('https://api.example.com' + a);
    return data.json();
}
