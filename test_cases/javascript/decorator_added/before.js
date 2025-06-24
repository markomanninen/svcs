// Before: No decorators (JavaScript doesn't have built-in decorators)
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
