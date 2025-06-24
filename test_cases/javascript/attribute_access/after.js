// After: Complex attribute access patterns
let user = { name: 'John', age: 30, profile: { avatar: 'pic.jpg' } };
let result = user.name;
let avatar = user.profile?.avatar;
let email = user?.contact?.email || 'unknown';

class Person {
    constructor(name) {
        this.name = name;
        this.metadata = { created: Date.now() };
    }
    
    getName() {
        return this.name;
    }
    
    getCreatedDate() {
        return new Date(this.metadata.created);
    }
    
    getProfile() {
        return this.profile?.settings?.theme || 'default';
    }
}

let person = new Person('Alice');
console.log(person.name);
console.log(person.metadata.created);
console.log(person.getProfile());
