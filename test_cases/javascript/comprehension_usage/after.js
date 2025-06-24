// After: Using array methods (JS equivalent of comprehensions)
let numbers = [1, 2, 3, 4, 5];

// Array comprehension equivalent using map
let doubled = numbers.map(n => n * 2);

// Filter comprehension
let filtered = numbers.filter(num => num % 2 === 0);

// Reduce for sum (comprehension equivalent)
let sum = numbers.reduce((acc, num) => acc + num, 0);

// Complex comprehension equivalents
let processed = numbers
    .filter(n => n > 2)
    .map(n => n * 3)
    .reduce((acc, n) => [...acc, n, n + 1], []);

// Object comprehension equivalent
let mapped = Object.fromEntries(
    numbers.map(n => [n, n * n])
);
