// Before: Basic assignment patterns
let user = null;
let data = {};

function processData() {
    user = getData();
    data.processed = true;
    let result = calculate();
    return result;
}

let counter = 0;
let items = [];
