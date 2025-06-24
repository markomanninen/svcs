// After: Class with static attributes and fields
class Calculator {
    static PI = 3.14159;
    static VERSION = '1.0.0';
    
    constructor() {
        this.instance_var = 0;
    }
    
    add(x, y) {
        return x + y;
    }
    
    static getConstants() {
        return { PI: Calculator.PI, VERSION: Calculator.VERSION };
    }
}

class MathUtils {
    static DEFAULT_PRECISION = 2;
    static MAX_VALUE = 999999;
    
    static helper() {
        return 'helping';
    }
    
    static format(value) {
        return value.toFixed(MathUtils.DEFAULT_PRECISION);
    }
}
