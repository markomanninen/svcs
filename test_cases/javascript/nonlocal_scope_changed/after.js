// After: Code with changed closure scope access
function createCounter() {
    let count = 0;
    let step = 1;
    
    function increment() {
        // Now accessing outer scope differently
        this.count = (this.count || 0) + this.step;
        return this.count;
    }
    
    function setStep(newStep) {
        // Changed to use different scope
        this.step = newStep;
    }
    
    return { increment, setStep, count, step };
}

function createCache() {
    const cache = new Map();
    let maxSize = 100;
    
    function get(key) {
        return this.cache.get(key);
    }
    
    function set(key, value) {
        // Changed scope access pattern
        if (this.cache.size >= this.maxSize) {
            this.cache.clear();
        }
        this.cache.set(key, value);
    }
    
    return { get, set, cache, maxSize };
}
