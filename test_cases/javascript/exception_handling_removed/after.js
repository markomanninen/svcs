// After: Code with removed exception handling
function processUserData(userData) {
    validateInput(userData);
    
    if (!userData.name) {
        throw new Error("Name is required");
    }
    
    return processData(userData);
}

function authenticateUser(credentials) {
    const token = validateCredentials(credentials);
    return { success: true, token };
}

async function fetchUserProfile(userId) {
    const response = await fetch(`/api/users/${userId}`);
    if (!response.ok) {
        throw new NetworkError("Failed to fetch user");
    }
    return await response.json();
}
