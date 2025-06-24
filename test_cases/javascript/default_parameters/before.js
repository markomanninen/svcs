// Before: Functions without default parameters
function greet(name) {
  name = name || 'Guest';
  return `Hello, ${name}!`;
}

function calculateTotal(price, quantity, tax) {
  quantity = quantity || 1;
  tax = tax || 0.1;
  return price * quantity * (1 + tax);
}

function createUser(username, email, role) {
  if (!role) {
    role = 'user';
  }
  return {
    username: username,
    email: email,
    role: role,
    createdAt: new Date()
  };
}

class ApiClient {
  constructor(baseUrl, timeout) {
    this.baseUrl = baseUrl || 'https://api.example.com';
    this.timeout = timeout || 3000;
  }
  
  fetchData(endpoint, options) {
    const fullOptions = options || {};
    // Simulate fetch
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
