// Enhanced JavaScript test for SVCS multi-language support

class Calculator {
    constructor(precision = 2) {
        this.precision = precision;
        this.history = [];
    }
    
    add(a, b) {
        const result = a + b;
        this.logOperation('add', a, b, result);
        return this.round(result);
    }
    
    multiply(a, b) {
        const result = a * b;
        this.logOperation('multiply', a, b, result);
        return this.round(result);
    }
    
    logOperation(op, a, b, result) {
        this.history.push({
            operation: op,
            operands: [a, b],
            result: result,
            timestamp: new Date()
        });
    }
    
    round(value) {
        return Math.round(value * Math.pow(10, this.precision)) / Math.pow(10, this.precision);
    }
}

function createCalculator(precision) {
    return new Calculator(precision);
}

const calc = createCalculator(3);
console.log(calc.add(5, 3));
