// After: Multiple return patterns with early returns
function getValue() {
    return 42;
}

function checkStatus(user) {
    if (!user) {
        return 'unknown';
    }
    
    if (user.suspended) {
        return 'suspended';
    }
    
    if (user.active) {
        return 'active';
    }
    
    if (user.pending) {
        return 'pending';
    }
    
    return 'inactive';
}

function processData(data) {
    if (!data) {
        return null;
    }
    
    if (data.error) {
        console.error('Data has error');
        return { error: data.error };
    }
    
    if (data.processed) {
        return { result: data.processed, cached: true };
    }
    
    const result = performProcessing(data);
    if (result.success) {
        return { result: result.data, cached: false };
    }
    
    return { error: 'Processing failed' };
}

function performProcessing(data) {
    return { success: true, data: data };
}
