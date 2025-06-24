// Before: Imperative JavaScript

function processArray(items) {
    const result = [];
    for (let i = 0; i < items.length; i++) {
        result.push(items[i] * 2);
    }
    return result;
}

function filterItems(items, minValue) {
    const result = [];
    for (let i = 0; i < items.length; i++) {
        if (items[i] > minValue) {
            result.push(items[i]);
        }
    }
    return result;
}

function sumItems(items) {
    let total = 0;
    for (let i = 0; i < items.length; i++) {
        total += items[i];
    }
    return total;
}

function findItem(items, predicate) {
    for (let i = 0; i < items.length; i++) {
        if (predicate(items[i])) {
            return items[i];
        }
    }
    return null;
}

function sortItems(items) {
    const result = [...items];
    result.sort(function(a, b) {
        return a - b;
    });
    return result;
}

class DataProcessor {
    constructor() {
        this.cache = {};
    }
    
    processItem(item) {
        return item * 2;
    }
    
    processItems(items) {
        const result = [];
        for (let i = 0; i < items.length; i++) {
            result.push(this.processItem(items[i]));
        }
        return result;
    }
}
