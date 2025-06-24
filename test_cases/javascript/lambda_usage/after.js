// After: Extensive use of lambda/arrow functions
function processItems(items) {
    return items.map(item => item * 2);
}

function filterData(data) {
    return data.filter(item => item.active);
}

// Additional lambda usage
const sortByName = (items) => items.sort((a, b) => a.name.localeCompare(b.name));

const createUser = (name, age) => ({ name, age, created: Date.now() });

const validateUsers = (users) => users.every(user => user.name && user.age > 0);

const processAsync = async (items) => {
    return await Promise.all(items.map(async item => {
        const processed = await processItem(item);
        return processed;
    }));
};

const composeFunctions = (...fns) => (value) => fns.reduce((acc, fn) => fn(acc), value);

const memoize = (fn) => {
    const cache = new Map();
    return (...args) => {
        const key = JSON.stringify(args);
        if (cache.has(key)) return cache.get(key);
        const result = fn(...args);
        cache.set(key, result);
        return result;
    };
};

// Higher-order functions with lambdas
const createMultiplier = (factor) => (value) => value * factor;
const double = createMultiplier(2);
const triple = createMultiplier(3);
