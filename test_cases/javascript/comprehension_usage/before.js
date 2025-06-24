// Before: No array/object comprehensions
let numbers = [1, 2, 3, 4, 5];
let doubled = [];
for (let i = 0; i < numbers.length; i++) {
    doubled.push(numbers[i] * 2);
}

let filtered = [];
for (let num of numbers) {
    if (num % 2 === 0) {
        filtered.push(num);
    }
}

let sum = 0;
for (let num of numbers) {
    sum += num;
}
