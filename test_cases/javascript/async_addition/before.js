// Before: Without async functions
function fetchData(url) {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({ data: 'example' });
        }, 1000);
    });
}

function processData(data) {
    return data.map(item => item.value);
}

function saveData(data) {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({ success: true });
        }, 500);
    });
}
