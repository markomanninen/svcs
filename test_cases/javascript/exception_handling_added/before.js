// Before: No exception handling
function processData(data) {
    return data.map(item => item.value);
}

function calculateTotal(items) {
    return items.reduce((sum, item) => sum + item.price, 0);
}

class DataProcessor {
    process(input) {
        return input.toString().toUpperCase();
    }
}
