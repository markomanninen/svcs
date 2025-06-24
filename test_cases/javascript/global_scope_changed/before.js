// Before: Code with local scope patterns
function setupApplication() {
    let config = { debug: false };
    const apiUrl = "localhost:3000";
    var isInitialized = false;
    
    function initialize() {
        const settings = loadSettings();
        let userData = null;
        isInitialized = true;
        return settings;
    }
    
    function processData(data) {
        const result = transform(data);
        let cache = new Map();
        return result;
    }
    
    return { initialize, processData };
}
