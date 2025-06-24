// Before: Regular functions
function createSequence(start, end) {
    const result = [];
    for (let i = start; i <= end; i++) {
        result.push(i);
    }
    return result;
}

function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

function processNumbers(numbers) {
    const results = [];
    for (let num of numbers) {
        results.push(num * 2);
    }
    return results;
}
