// After: Code with error handling removed
function processFile(filename) {
    const content = readFile(filename);
    return processContent(content);
}

function connectToDatabase() {
    const connection = establishConnection();
    return connection;
}
