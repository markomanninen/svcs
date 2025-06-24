// Before: Functional JavaScript with map, filter, reduce

function processData(items) {
    // Using functional programming patterns
    return items
        .filter(item => item.active)
        .map(item => ({ ...item, processed: true }))
        .reduce((acc, item) => {
            acc[item.category] = acc[item.category] || [];
            acc[item.category].push(item);
            return acc;
        }, {});
}

function calculateStats(numbers) {
    const doubled = numbers.map(n => n * 2);
    const evens = doubled.filter(n => n % 2 === 0);
    const sum = evens.reduce((acc, n) => acc + n, 0);
    return sum;
}

// Higher-order functions
const withLogging = (fn) => (...args) => {
    console.log('Calling function with args:', args);
    const result = fn(...args);
    console.log('Function returned:', result);
    return result;
};

const compose = (f, g) => (x) => f(g(x));
const pipe = (...fns) => (value) => fns.reduce((acc, fn) => fn(acc), value);

// Usage
const loggedProcess = withLogging(processData);
const transform = compose(
    x => x.toUpperCase(),
    x => x.trim()
);
