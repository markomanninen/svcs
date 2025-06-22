<?php

namespace App\Example;

use DateTime;
use Exception;

/**
 * Demo class for enhanced PHP analysis
 * Now with additional features
 */
class DemoClass implements DemoInterface {
    public string $name;
    private $data = [];
    protected static int $instanceCount = 0;
    
    public function __construct(string $name) {
        $this->name = $name;
        self::$instanceCount++;
    }
    
    public function getData(): array {
        return $this->data;
    }
    
    public function setData(array $data): void {
        $this->data = $data;
    }
    
    public function process(): bool {
        return !empty($this->data);
    }
    
    public static function getInstanceCount(): int {
        return self::$instanceCount;
    }
}

function simpleFunction(string $param): string {
    return "Hello " . $param;
}

function newAdvancedFunction(array $items, ?string $prefix = null): array {
    return array_map(function($item) use ($prefix) {
        return ($prefix ?? '') . $item;
    }, $items);
}

interface DemoInterface {
    public function process(): bool;
}

trait DemoTrait {
    protected function helperMethod(): bool {
        return true;
    }
    
    protected function newTraitMethod(string $data): array {
        return explode(',', $data);
    }
}

define('DEMO_CONSTANT', 'updated_value');
define('NEW_CONSTANT', 42);
