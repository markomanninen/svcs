// After: Removed assertions, added proper validation
function validateUser(user) {
    if (!user) {
        throw new Error('User should not be null');
    }
    if (!user.name) {
        throw new Error('User should have a name');
    }
    if (user.age < 0) {
        throw new Error('User age should be non-negative');
    }
    
    return {
        id: user.id,
        name: user.name,
        isValid: true
    };
}

class UserValidator {
    validate(user) {
        if (typeof user !== 'object') {
            throw new TypeError('User must be an object');
        }
        return user;
    }
}
