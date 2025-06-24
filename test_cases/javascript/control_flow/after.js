// After: Complex control flow with multiple conditions and loops
function processValue(x) {
    if (x > 100) {
        return x * 3;
    } else if (x > 50) {
        return x * 2;
    } else if (x > 0) {
        return x * 1.5;
    } else {
        return 0;
    }
}

function loopData(items) {
    for (let i = 0; i < items.length; i++) {
        console.log(items[i]);
    }
    
    // Added new control structures
    for (let item of items) {
        if (item.type === 'special') {
            continue;
        }
        
        while (item.processing) {
            item.step++;
            if (item.step > 10) break;
        }
        
        switch (item.category) {
            case 'A':
                item.priority = 1;
                break;
            case 'B':
                item.priority = 2;
                break;
            default:
                item.priority = 3;
        }
    }
}
