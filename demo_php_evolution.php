<?php

// Simple PHP file to demonstrate semantic evolution
class Calculator {
    public function add($a, $b) {
        return $a + $b;
    }
    
    public function multiply($a, $b) {
        return $a * $b;
    }
}

function greet($name) {
    return "Hello " . $name;
}

$calc = new Calculator();
echo $calc->add(5, 3);
echo greet("World");

?>
