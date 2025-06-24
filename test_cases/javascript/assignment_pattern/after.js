// After: Complex assignment patterns with destructuring
let user = null;
let data = {};

function processData() {
    const { userData, metadata } = getData();
    user = userData;
    data = { ...data, ...metadata, processed: true };
    
    const [first, second, ...rest] = calculate();
    const { result, error } = validateResult(first);
    
    return { result, error, remaining: rest };
}

let [counter, multiplier] = [0, 1];
let items = new Set();
const { x: posX, y: posY } = getPosition();
