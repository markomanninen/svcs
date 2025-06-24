// After: Functions with default parameters
function greet(name = 'Guest') {
  return `Hello, ${name}!`;
}

function calculateTotal(price, quantity = 1, tax = 0.1) {
  return price * quantity * (1 + tax);
}

function createUser(username, email, role = 'user') {
  return {
    username,
    email,
    role,
    createdAt: new Date()
  };
}

class ApiClient {
  constructor(baseUrl = 'https://api.example.com', timeout = 3000) {
    this.baseUrl = baseUrl;
    this.timeout = timeout;
  }
  
  fetchData(endpoint, options = {}) {
    // Simulate fetch with destructuring and defaults
    console.log(`Fetching ${this.baseUrl}/${endpoint} with timeout ${this.timeout}`);
    return Promise.resolve({ data: 'example' });
  }
}

// Usage
const greeting = greet();
const total = calculateTotal(29.99);
const user = createUser('johndoe', 'john@example.com');
const client = new ApiClient();
client.fetchData('users');
