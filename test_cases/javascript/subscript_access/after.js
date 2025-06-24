// After: Complex subscript access patterns
let items = [1, 2, 3, 4, 5];
let first = items[0];
let last = items[items.length - 1];

// Added destructuring array access
let [head, ...tail] = items;
let [a, b, c] = items;

function getItem(arr, index) {
    return arr[index];
}

// Complex nested access
let data = { 
    users: ['Alice', 'Bob'], 
    profiles: [
        { name: 'Alice', settings: { theme: 'dark' } },
        { name: 'Bob', settings: { theme: 'light' } }
    ]
};

let user = data.users[0];
let firstProfile = data.profiles[0];
let firstTheme = data.profiles[0].settings.theme;
let themes = data.profiles.map(p => p.settings.theme);

// Dynamic property access
let key = 'users';
let dynamicData = data[key];

// Multiple levels of array/object access
let matrix = [[1, 2], [3, 4], [5, 6]];
let element = matrix[1][0];

// Computed property access
let prop = 'length';
let size = items[prop];

// Optional chaining with arrays
let safeAccess = data.profiles?.[0]?.settings?.theme;
