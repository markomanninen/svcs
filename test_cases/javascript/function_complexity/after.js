// After: Increased function complexity with multiple conditions and nested logic
function add(a, b) {
    return a + b;
}

function processItem(item) {
    if (!item) {
        return null;
    }
    
    if (item.type === 'premium') {
        if (item.status === 'active') {
            if (item.permissions && item.permissions.length > 0) {
                return item.permissions.includes('read') ? item.name : 'Restricted';
            } else {
                return 'No permissions';
            }
        } else {
            return 'Inactive premium';
        }
    } else if (item.type === 'standard') {
        return item.name || 'Standard user';
    } else {
        return 'Unknown type';
    }
}

function simpleLoop(items) {
    for (let item of items) {
        console.log(item);
        
        // Added complex nested logic
        if (item.category) {
            switch (item.category) {
                case 'A':
                    if (item.priority > 5) {
                        for (let i = 0; i < item.retries; i++) {
                            if (item.attempts[i].success) {
                                console.log('Success found');
                                break;
                            } else {
                                continue;
                            }
                        }
                    }
                    break;
                case 'B':
                    while (item.processing && item.steps < 10) {
                        item.steps++;
                        if (item.steps % 2 === 0) {
                            item.processing = false;
                        }
                    }
                    break;
                default:
                    if (item.fallback) {
                        item.processed = true;
                    }
            }
        }
    }
}
