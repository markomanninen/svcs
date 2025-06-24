// After: Functional JavaScript

// Using arrow functions and map
const processArray = items => items.map(item => item * 2);

// Using filter
const filterItems = (items, minValue) => items.filter(item => item > minValue);

// Using reduce
const sumItems = items => items.reduce((total, item) => total + item, 0);

// Using find
const findItem = (items, predicate) => items.find(predicate);

// Using sort with arrow function
const sortItems = items => [...items].sort((a, b) => a - b);

// Higher-order functions and function composition
const compose = (...fns) => x => fns.reduceRight((v, f) => f(v), x);
const pipe = (...fns) => x => fns.reduce((v, f) => f(v), x);

// Currying
const curry = (fn) => {
    const arity = fn.length;
    return function curried(...args) {
        if (args.length >= arity) {
            return fn(...args);
        }
        return (...moreArgs) => curried(...args, ...moreArgs);
    };
};

// Memoization
const memoize = (fn) => {
    const cache = new Map();
    return (...args) => {
        const key = JSON.stringify(args);
        if (cache.has(key)) {
            return cache.get(key);
        }
        const result = fn(...args);
        cache.set(key, result);
        return result;
    };
};

// Functional class replacement
const createDataProcessor = () => {
    const cache = {};
    
    const processItem = memoize(item => item * 2);
    
    const processItems = items => items.map(processItem);
    
    return {
        processItem,
        processItems
    };
};

// Example of function composition
const processAndSum = items => {
    return pipe(
        arr => arr.filter(x => x > 0),
        arr => arr.map(x => x * 2),
        arr => arr.reduce((sum, x) => sum + x, 0)
    )(items);
};
