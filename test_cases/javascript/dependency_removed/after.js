// After: Removed dependencies, implemented functionality natively
const app = createSimpleServer();

function createSimpleServer() {
    return {
        use: (middleware) => console.log('Using middleware'),
        listen: (port) => console.log(`Server on port ${port}`)
    };
}

const userSchema = {
    name: 'String',
    email: 'String'
};

function processUsers(users) {
    // Replaced lodash.uniqBy with native implementation
    const seen = new Set();
    return users.filter(user => {
        if (seen.has(user.email)) {
            return false;
        }
        seen.add(user.email);
        return true;
    });
}
