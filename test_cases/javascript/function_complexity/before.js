// Before: Simple function complexity
function add(a, b) {
    return a + b;
}

function processItem(item) {
    if (item) {
        return item.name;
    }
    return null;
}

function simpleLoop(items) {
    for (let item of items) {
        console.log(item);
    }
}
