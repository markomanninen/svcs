// Before: Synchronous functions
function fetchData(url) {
    // Simulating sync operation
    return { data: 'example' };
}

function processResults(data) {
    return data.map(item => item.value);
}

class DataService {
    getData() {
        return this.fetchFromAPI();
    }
    
    fetchFromAPI() {
        return { result: 'success' };
    }
}
