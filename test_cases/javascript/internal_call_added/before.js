// Before: Functions without internal calls
function calculateArea(radius) {
    return 3.14159 * radius * radius;
}

function formatName(firstName, lastName) {
    return firstName + ' ' + lastName;
}

class Calculator {
    add(a, b) {
        return a + b;
    }
    
    multiply(a, b) {
        return a * b;
    }
}
