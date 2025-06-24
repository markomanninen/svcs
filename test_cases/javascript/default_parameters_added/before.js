// Before: Functions without default parameters
function greet(name, greeting) {
    return `${greeting}, ${name}!`;
}

class Calculator {
    constructor(precision) {
        this.precision = precision;
    }
    
    format(value, decimals) {
        return value.toFixed(decimals);
    }
}

const processData = (data, options) => {
    return data;
};
