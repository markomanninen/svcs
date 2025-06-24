// Before: Class without static attributes
class Calculator {
    constructor() {
        this.instance_var = 0;
    }
    
    add(x, y) {
        return x + y;
    }
}

class MathUtils {
    static helper() {
        return 'helping';
    }
}
