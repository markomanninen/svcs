// Before: No inheritance
class Animal {
    constructor(name) {
        this.name = name;
    }
    
    speak() {
        return `${this.name} makes a sound`;
    }
}

class Vehicle {
    constructor(brand) {
        this.brand = brand;
    }
}
