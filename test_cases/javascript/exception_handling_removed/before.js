// Before: Code with comprehensive exception handling
function processUserData(userData) {
    try {
        validateInput(userData);
        
        if (!userData.name) {
            throw new Error("Name is required");
        }
        
        return processData(userData);
    } catch (error) {
        if (error instanceof ValidationError) {
            console.error("Validation failed:", error);
            throw new ValidationError("Invalid user data");
        } else if (error instanceof TypeError) {
            console.error("Type error:", error);
            return null;
        } else {
            console.error("General error:", error);
            throw error;
        }
    }
}

function authenticateUser(credentials) {
    try {
        const token = validateCredentials(credentials);
        return { success: true, token };
    } catch (error) {
        if (error instanceof AuthenticationError) {
            return { success: false, error: "Authentication failed" };
        } else if (error instanceof NetworkError) {
            return { success: false, error: "Network unavailable" };
        } else {
            throw error;
        }
    }
}

async function fetchUserProfile(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        if (!response.ok) {
            throw new NetworkError("Failed to fetch user");
        }
        return await response.json();
    } catch (error) {
        if (error instanceof NetworkError) {
            console.log("Network error occurred");
            return null;
        } else if (error instanceof SyntaxError) {
            console.log("JSON parsing failed");
            return null;
        } else {
            throw error;
        }
    }
}
