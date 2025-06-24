// After: Converted functions to async
async function fetchData(url) {
    // Now async operation
    const response = await fetch(url);
    return await response.json();
}

async function processResults(data) {
    return await Promise.all(
        data.map(async item => {
            const processed = await processItem(item);
            return processed.value;
        })
    );
}

class DataService {
    async getData() {
        return await this.fetchFromAPI();
    }
    
    async fetchFromAPI() {
        await new Promise(resolve => setTimeout(resolve, 100));
        return { result: 'success' };
    }
}

// Additional async functions
async function processItem(item) {
    return new Promise(resolve => {
        setTimeout(() => resolve(item), 50);
    });
}
