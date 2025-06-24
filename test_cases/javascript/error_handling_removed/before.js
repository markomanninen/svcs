// Before: Code with error handling patterns
function processFile(filename) {
    try {
        const content = readFile(filename);
        return processContent(content);
    } catch (error) {
        console.error("File processing failed:", error);
        throw new Error("Processing failed");
    }
}

function connectToDatabase() {
    try {
        const connection = establishConnection();
        return connection;
    } catch (error) {
        console.error("Database connection failed:", error);
        return null;
    }
}
