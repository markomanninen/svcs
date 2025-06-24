// After: Imperative JavaScript without functional patterns

function processData(items) {
    // Using imperative programming instead
    const result = {};
    for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if (item.active) {
            const processedItem = {
                id: item.id,
                name: item.name,
                category: item.category,
                processed: true
            };
            
            if (!result[item.category]) {
                result[item.category] = [];
            }
            result[item.category].push(processedItem);
        }
    }
    return result;
}

function calculateStats(numbers) {
    let sum = 0;
    for (let i = 0; i < numbers.length; i++) {
        const doubled = numbers[i] * 2;
        if (doubled % 2 === 0) {
            sum += doubled;
        }
    }
    return sum;
}

// Regular functions instead of higher-order functions
function logFunction(fn, name, args) {
    console.log('Calling function ' + name + ' with args:', args);
    const result = fn.apply(null, args);
    console.log('Function returned:', result);
    return result;
}

function transformString(str) {
    const trimmed = str.trim();
    return trimmed.toUpperCase();
}

// Usage
function processDataWithLogging(items) {
    return logFunction(processData, 'processData', [items]);
}
