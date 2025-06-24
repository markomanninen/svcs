// Before: JavaScript testing with console.assert
function validateUser(user) {
    console.assert(user != null, 'User should not be null');
    console.assert(user.name, 'User should have a name');
    console.assert(user.age >= 0, 'User age should be non-negative');
    
    return {
        id: user.id,
        name: user.name,
        isValid: true
    };
}

class UserValidator {
    validate(user) {
        console.assert(typeof user === 'object', 'User must be an object');
        return user;
    }
}
