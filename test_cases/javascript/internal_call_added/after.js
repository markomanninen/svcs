// After: Functions with internal method calls
function calculateArea(radius) {
    const pi = getPiValue();
    return pi * Math.pow(radius, 2);
}

function getPiValue() {
    return 3.14159;
}

function formatName(firstName, lastName) {
    const trimmedFirst = trimString(firstName);
    const trimmedLast = trimString(lastName);
    return combineNames(trimmedFirst, trimmedLast);
}

function trimString(str) {
    return str.trim();
}

function combineNames(first, last) {
    return first + ' ' + last;
}

class Calculator {
    add(a, b) {
        this.validate(a);
        this.validate(b);
        return this.performAddition(a, b);
    }
    
    multiply(a, b) {
        this.validate(a);
        this.validate(b);
        return this.performMultiplication(a, b);
    }
    
    validate(value) {
        if (typeof value !== 'number') {
            throw new Error('Value must be a number');
        }
    }
    
    performAddition(a, b) {
        return a + b;
    }
    
    performMultiplication(a, b) {
        return a * b;
    }
}
