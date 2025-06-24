// Before: Simple return patterns
function getValue() {
    return 42;
}

function checkStatus(user) {
    if (user.active) {
        return 'active';
    }
    return 'inactive';
}

function processData(data) {
    return data.processed;
}
