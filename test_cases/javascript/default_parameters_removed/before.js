// Before: Functions with default parameters
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

// Usage
const greeting = greet();
const total = calculateTotal(29.99);
const user = createUser('johndoe', 'john@example.com');
