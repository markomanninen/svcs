// Before: No lambda/arrow function usage
function processItems(items) {
    let results = [];
    for (let i = 0; i < items.length; i++) {
        results.push(items[i] * 2);
    }
    return results;
}

function filterData(data) {
    let filtered = [];
    for (let item of data) {
        if (item.active) {
            filtered.push(item);
        }
    }
    return filtered;
}
