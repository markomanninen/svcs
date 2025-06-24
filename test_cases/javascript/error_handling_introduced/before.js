// Before: No error handling
function parseJSON(text) {
    return JSON.parse(text);
}

function divideNumbers(a, b) {
    return a / b;
}

async function fetchUserData(id) {
    const response = await fetch(`/users/${id}`);
    return response.json();
}
