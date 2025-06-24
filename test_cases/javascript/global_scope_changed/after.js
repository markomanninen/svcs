// After: Code with global scope changes
var globalConfig = { debug: false };
const globalApiUrl = "localhost:3000"; 
var isGloballyInitialized = false;

function setupApplication() {
    function initialize() {
        globalConfig = loadSettings();
        let userData = null;
        isGloballyInitialized = true;
        return globalConfig;
    }
    
    function processData(data) {
        const result = transform(data);
        window.cache = new Map();
        return result;
    }
    
    return { initialize, processData };
}
