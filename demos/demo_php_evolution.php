<?php

namespace App\Math;

use DateTime;
use Exception;

// Enhanced PHP file to demonstrate semantic evolution
abstract class AbstractCalculator {
    protected $history = [];
    protected $precision = 2;
    
    abstract public function calculate($operation, $a, $b);
    
    protected function logOperation($operation, $a, $b, $result) {
        $this->history[] = [
            'operation' => $operation,
            'operands' => [$a, $b],
            'result' => round($result, $this->precision),
            'timestamp' => new DateTime()
        ];
    }
    
    public function getHistory() {
        return $this->history;
    }
    
    public function setPrecision(int $precision): void {
        $this->precision = $precision;
    }
}

class Calculator extends AbstractCalculator {
    private const MAX_HISTORY = 100;
    
    public function __construct(int $precision = 2) {
        $this->history = [];
        $this->precision = $precision;
    }
    
    public function calculate($operation, $a, $b) {
        switch ($operation) {
            case 'add':
                return $this->add($a, $b);
            case 'multiply':
                return $this->multiply($a, $b);
            case 'divide':
                return $this->divide($a, $b);
            case 'subtract':
                return $this->subtract($a, $b);
            default:
                throw new Exception("Unsupported operation: $operation");
        }
    }
    
    public function add($a, $b) {
        $result = $a + $b;
        $this->logOperation('add', $a, $b, $result);
        $this->trimHistory();
        return $result;
    }
    
    public function subtract($a, $b) {
        $result = $a - $b;
        $this->logOperation('subtract', $a, $b, $result);
        $this->trimHistory();
        return $result;
    }
    
    public function multiply($a, $b) {
        $result = $a * $b;
        $this->logOperation('multiply', $a, $b, $result);
        $this->trimHistory();
        return $result;
    }
    
    public function divide($a, $b) {
        if ($b == 0) {
            throw new \InvalidArgumentException("Division by zero");
        }
        $result = $a / $b;
        $this->logOperation('divide', $a, $b, $result);
        $this->trimHistory();
        return $result;
    }
    
    private function trimHistory(): void {
        if (count($this->history) > self::MAX_HISTORY) {
            $this->history = array_slice($this->history, -self::MAX_HISTORY);
        }
    }
    
    public function clearHistory(): void {
        $this->history = [];
    }
}

interface GreeterInterface {
    public function greet(string $name): string;
}

trait TimestampTrait {
    private $lastUsed;
    
    public function touch(): void {
        $this->lastUsed = new DateTime();
    }
    
    public function getLastUsed(): ?DateTime {
        return $this->lastUsed;
    }
}

class Greeter implements GreeterInterface {
    use TimestampTrait;
    
    private $greeting = "Hello";
    private $punctuation = "!";
    
    public function greet(string $name): string {
        $this->touch();
        return $this->greeting . " " . $name . $this->punctuation;
    }
    
    public function setGreeting(string $greeting): void {
        $this->greeting = $greeting;
    }
    
    public function setPunctuation(string $punctuation): void {
        $this->punctuation = $punctuation;
    }
}

function greet($name) {
    return "Hello " . $name;
}

function create_calculator(int $precision = 2): Calculator {
    return new Calculator($precision);
}

function calculate_average(array $numbers): float {
    if (empty($numbers)) {
        throw new Exception("Cannot calculate average of empty array");
    }
    
    return array_sum($numbers) / count($numbers);
}

// Usage examples
$calc = create_calculator(3);
echo $calc->calculate('add', 5, 3) . "\n";
echo $calc->calculate('multiply', 2, 4) . "\n";
echo $calc->calculate('subtract', 10, 3) . "\n";

$greeter = new Greeter();
$greeter->setGreeting("Welcome");
$greeter->setPunctuation("!!!");
echo $greeter->greet("PHP World") . "\n";

$numbers = [1, 2, 3, 4, 5];
echo "Average: " . calculate_average($numbers) . "\n";

?>
