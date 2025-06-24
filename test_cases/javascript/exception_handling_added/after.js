// After: Added exception handling with try/catch blocks
function processData(data) {
    try {
        if (!Array.isArray(data)) {
            throw new TypeError('Data must be an array');
        }
        return data.map(item => {
            if (!item || typeof item.value === 'undefined') {
                throw new Error('Invalid item structure');
            }
            return item.value;
        });
    } catch (error) {
        console.error('Processing error:', error.message);
        return [];
    }
}

function calculateTotal(items) {
    try {
        if (!items || items.length === 0) {
            throw new Error('Items array is empty');
        }
        return items.reduce((sum, item) => {
            if (typeof item.price !== 'number') {
                throw new TypeError('Item price must be a number');
            }
            return sum + item.price;
        }, 0);
    } catch (error) {
        console.error('Calculation error:', error.message);
        return 0;
    }
}

class DataProcessor {
    process(input) {
        try {
            if (input === null || input === undefined) {
                throw new Error('Input cannot be null or undefined');
            }
            return input.toString().toUpperCase();
        } catch (error) {
            if (error instanceof TypeError) {
                console.error('Type error in processing:', error.message);
            } else {
                console.error('Processing error:', error.message);
            }
            return '';
        }
    }
}
