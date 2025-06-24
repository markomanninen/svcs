// After: Added comprehensive error handling
function parseJSON(text) {
    try {
        return JSON.parse(text);
    } catch (error) {
        console.error('JSON parsing failed:', error.message);
        return null;
    }
}

function divideNumbers(a, b) {
    try {
        if (b === 0) {
            throw new Error('Division by zero');
        }
        return a / b;
    } catch (error) {
        console.error('Division error:', error.message);
        return NaN;
    }
}

async function fetchUserData(id) {
    try {
        const response = await fetch(`/users/${id}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        if (error.name === 'TypeError') {
            console.error('Network error:', error.message);
        } else {
            console.error('Fetch error:', error.message);
        }
        throw error;
    }
}
