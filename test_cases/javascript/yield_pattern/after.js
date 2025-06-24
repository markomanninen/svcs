// After: Generator functions with various yield patterns
function* createNumbers() {
    yield 1;
    yield 2;
    yield 3;
    yield 4;
    yield 5;
}

function* processSequence(data) {
    for (let item of data) {
        yield item * 2;
    }
}

// Additional yield patterns
function* fibonacci() {
    let a = 0, b = 1;
    while (true) {
        yield a;
        [a, b] = [b, a + b];
    }
}

function* range(start, end) {
    for (let i = start; i < end; i++) {
        yield i;
    }
}

function* batchProcessor(items, batchSize) {
    for (let i = 0; i < items.length; i += batchSize) {
        yield items.slice(i, i + batchSize);
    }
}

// Yield with value and delegation
function* complexGenerator() {
    yield 'first';
    yield* range(1, 4);  // yield delegation
    yield 'last';
}

// Async generator
async function* asyncGenerator() {
    for (let i = 0; i < 3; i++) {
        await new Promise(resolve => setTimeout(resolve, 100));
        yield `async-${i}`;
    }
}
