// After: With async functions
async function fetchData(url) {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({ data: 'example' });
        }, 1000);
    });
}

async function processData(data) {
    const processed = await Promise.all(
        data.map(async item => {
            const value = await transformItem(item);
            return value;
        })
    );
    return processed;
}

async function saveData(data) {
    const result = await fetch('/api/save', {
        method: 'POST',
        body: JSON.stringify(data)
    });
    return await result.json();
}

async function transformItem(item) {
    return new Promise(resolve => {
        setTimeout(() => resolve(item.value * 2), 100);
    });
}
