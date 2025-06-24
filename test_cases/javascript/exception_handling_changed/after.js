// After: Code with changed exception handling (different catch types)
function processApiRequest(data) {
    try {
        validateApiData(data);
        return sendRequest(data);
    } catch (error) {
        if (error instanceof TypeError) {
            console.error("Type error occurred");
            return { error: "Type mismatch" };
        } else if (error instanceof ReferenceError) {
            console.error("Reference error occurred");
            return { error: "Reference issue" };
        } else {
            console.error("General error occurred");
            return { error: "General failure" };
        }
    }
}

function parseConfiguration(config) {
    try {
        return JSON.parse(config);
    } catch (error) {
        console.error("Parsing failed");
        return {};
    }
}
