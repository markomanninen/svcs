// After: Functions with default parameters added
function greet(name = 'World', greeting = 'Hello') {
    return `${greeting}, ${name}!`;
}

function createUser(name, age = 18, role = 'user', active = true) {
    return { name, age, role, active };
}

function processArray(arr, mapper = x => x, filter = () => true) {
    return arr.filter(filter).map(mapper);
}

class Calculator {
    constructor(precision = 2) {
        this.precision = precision;
    }
    
    format(value, decimals = this.precision) {
        return value.toFixed(decimals);
    }
    
    calculate(a, b, operation = 'add', round = true) {
        let result;
        switch (operation) {
            case 'add': result = a + b; break;
            case 'multiply': result = a * b; break;
            default: result = 0;
        }
        return round ? Math.round(result) : result;
    }
}

const processData = (data, options = { validate: true, transform: false }) => {
    return data;
};

const fetchData = async (url, timeout = 5000, retries = 3) => {
    // fetch with timeout and retries
    return fetch(url);
};
