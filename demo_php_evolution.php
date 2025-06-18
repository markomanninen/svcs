<?php

namespace App\Math;

use DateTime;

// Enhanced PHP file to demonstrate semantic evolution
class Calculator {
    private $history = [];
    
    public function __construct() {
        $this->history = [];
    }
    
    public function add($a, $b) {
        $result = $a + $b;
        $this->logOperation('add', $a, $b, $result);
        return $result;
    }
    
    public function multiply($a, $b) {
        $result = $a * $b;
        $this->logOperation('multiply', $a, $b, $result);
        return $result;
    }
    
    public function divide($a, $b) {
        if ($b == 0) {
            throw new \InvalidArgumentException("Division by zero");
        }
        $result = $a / $b;
        $this->logOperation('divide', $a, $b, $result);
        return $result;
    }
    
    private function logOperation($operation, $a, $b, $result) {
        $this->history[] = [
            'operation' => $operation,
            'operands' => [$a, $b],
            'result' => $result,
            'timestamp' => new DateTime()
        ];
    }
    
    public function getHistory() {
        return $this->history;
    }
}

interface GreeterInterface {
    public function greet(string $name): string;
}

class Greeter implements GreeterInterface {
    private $greeting = "Hello";
    
    public function greet(string $name): string {
        return $this->greeting . " " . $name . "!";
    }
    
    public function setGreeting(string $greeting): void {
        $this->greeting = $greeting;
    }
}

function greet($name) {
    return "Hello " . $name;
}

function create_calculator(): Calculator {
    return new Calculator();
}

// Usage
$calc = create_calculator();
echo $calc->add(5, 3);
echo $calc->multiply(2, 4);

$greeter = new Greeter();
echo $greeter->greet("World");
echo greet("PHP");

?>
