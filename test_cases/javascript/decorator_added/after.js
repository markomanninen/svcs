// After: Added decorator-like patterns (higher-order functions)
function withLogging(target, propertyKey, descriptor) {
    const originalMethod = descriptor.value;
    descriptor.value = function(...args) {
        console.log(`Calling ${propertyKey} with args:`, args);
        const result = originalMethod.apply(this, args);
        console.log(`${propertyKey} returned:`, result);
        return result;
    };
    return descriptor;
}

function withCaching(target, propertyKey, descriptor) {
    const cache = new Map();
    const originalMethod = descriptor.value;
    descriptor.value = function(...args) {
        const key = JSON.stringify(args);
        if (cache.has(key)) {
            return cache.get(key);
        }
        const result = originalMethod.apply(this, args);
        cache.set(key, result);
        return result;
    };
    return descriptor;
}

class UserService {
    getUser(id) {
        return fetch(`/users/${id}`).then(r => r.json());
    }
    
    saveUser(user) {
        return fetch('/users', {
            method: 'POST',
            body: JSON.stringify(user)
        });
    }
}

// Apply decorators manually (simulate decorator syntax)
withLogging(UserService.prototype, 'getUser', 
    Object.getOwnPropertyDescriptor(UserService.prototype, 'getUser'));
withCaching(UserService.prototype, 'saveUser', 
    Object.getOwnPropertyDescriptor(UserService.prototype, 'saveUser'));
