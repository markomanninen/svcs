// After: Regular functions instead of generators
function generateNumbers(start, end) {
    const result = [];
    for (let i = start; i <= end; i++) {
        result.push(i);
    }
    return result;
}

function generateFibonacci(count = 10) {
    const result = [];
    let a = 0, b = 1;
    for (let i = 0; i < count; i++) {
        result.push(a);
        [a, b] = [b, a + b];
    }
    return result;
}

function processItems(items) {
    return items.map(item => item.toUpperCase());
}

// Usage
const numbers = generateNumbers(1, 5);
const firstTenFib = generateFibonacci(10);
const processedItems = processItems(['hello', 'world']);
