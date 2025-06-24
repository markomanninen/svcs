// Before: Code with closure scope patterns
function createCounter() {
    let count = 0;
    let step = 1;
    
    function increment() {
        count += step;
        return count;
    }
    
    function setStep(newStep) {
        step = newStep;
    }
    
    return { increment, setStep };
}

function createCache() {
    const cache = new Map();
    let maxSize = 100;
    
    function get(key) {
        return cache.get(key);
    }
    
    function set(key, value) {
        if (cache.size >= maxSize) {
            cache.clear();
        }
        cache.set(key, value);
    }
    
    return { get, set };
}
