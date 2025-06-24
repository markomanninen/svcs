// Before: Generator functions
function* generateNumbers(start, end) {
    for (let i = start; i <= end; i++) {
        yield i;
    }
}

function* generateFibonacci() {
    let a = 0, b = 1;
    while (true) {
        yield a;
        [a, b] = [b, a + b];
    }
}

function* processItems(items) {
    for (const item of items) {
        yield item.toUpperCase();
    }
}

// Usage
const numbers = Array.from(generateNumbers(1, 5));
const firstTenFib = Array.from(generateFibonacci()).slice(0, 10);
const processedItems = Array.from(processItems(['hello', 'world']));
