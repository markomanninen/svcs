// Before: No generator yield patterns
function createNumbers() {
    return [1, 2, 3, 4, 5];
}

function processSequence(data) {
    let results = [];
    for (let item of data) {
        results.push(item * 2);
    }
    return results;
}
