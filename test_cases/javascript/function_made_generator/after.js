// After: Converted to generator functions
function* createSequence(start, end) {
    for (let i = start; i <= end; i++) {
        yield i;
    }
}

function* fibonacci(n) {
    let a = 0, b = 1;
    for (let i = 0; i < n; i++) {
        yield a;
        [a, b] = [b, a + b];
    }
}

function* processNumbers(numbers) {
    for (let num of numbers) {
        yield num * 2;
    }
}

// Additional generator functions
function* infiniteCounter(start = 0) {
    let count = start;
    while (true) {
        yield count++;
    }
}

function* batchProcessor(items, batchSize = 3) {
    for (let i = 0; i < items.length; i += batchSize) {
        yield items.slice(i, i + batchSize);
    }
}
