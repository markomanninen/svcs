// After: Functions without default parameters
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

// Usage
const greeting = greet();
const total = calculateTotal(29.99);
const user = createUser('johndoe', 'john@example.com');
