// Before: Code with specific exception handling
function processApiRequest(data) {
    try {
        validateApiData(data);
        return sendRequest(data);
    } catch (error) {
        if (error instanceof ValidationError) {
            console.error("Validation failed");
            return { error: "Invalid data" };
        } else if (error instanceof NetworkError) {
            console.error("Network failed");
            return { error: "Network issue" };
        }
    }
}

function parseConfiguration(config) {
    try {
        return JSON.parse(config);
    } catch (error) {
        if (error instanceof SyntaxError) {
            console.error("JSON parsing failed");
            return {};
        }
    }
}
