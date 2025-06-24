// After: Using augmented assignment operators
let counter = 0;
let total = 100;

function increment() {
    counter += 1;      // Changed from counter = counter + 1
    total *= 2;        // Changed from total = total * 2
}

let data = { score: 50 };
data.score += 10;      // Changed from data.score = data.score + 10

// Additional augmented assignments
let values = [1, 2, 3];
let result = 1;
result += 5;    // addition assignment
result -= 2;    // subtraction assignment
result *= 3;    // multiplication assignment
result /= 2;    // division assignment
result %= 7;    // modulo assignment
