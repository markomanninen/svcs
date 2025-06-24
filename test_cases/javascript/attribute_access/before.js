// Before: Basic attribute access
let user = { name: 'John', age: 30 };
let result = user.name;

class Person {
    constructor(name) {
        this.name = name;
    }
    
    getName() {
        return this.name;
    }
}

let person = new Person('Alice');
console.log(person.name);
