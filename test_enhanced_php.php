<?php

namespace App\Example;

use DateTime;
use Exception;

/**
 * Demo class for enhanced PHP analysis
 */
class DemoClass {
    public string $name;
    private $data = [];
    
    public function __construct(string $name) {
        $this->name = $name;
    }
    
    public function getData(): array {
        return $this->data;
    }
    
    public function setData(array $data): void {
        $this->data = $data;
    }
}

function simpleFunction($param) {
    return "Hello " . $param;
}

interface DemoInterface {
    public function process(): bool;
}

trait DemoTrait {
    protected function helperMethod() {
        return true;
    }
}

define('DEMO_CONSTANT', 'initial_value');
