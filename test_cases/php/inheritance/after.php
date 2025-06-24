<?php
// After: Completely restructured inheritance and composition

// Interfaces
interface Controller {
    public function index();
    public function show($id);
}

interface CreatableController {
    public function create($data);
}

interface UpdatableController {
    public function update($id, $data);
}

interface ValidatorInterface {
    public function validate($data): bool;
}

// Traits
trait LoggableTrait {
    protected function log($message) {
        // Log implementation
        error_log($message);
    }
}

trait CachableTrait {
    protected $cache = [];
    
    protected function getFromCache($key) {
        return $this->cache[$key] ?? null;
    }
    
    protected function saveToCache($key, $value) {
        $this->cache[$key] = $value;
    }
}

// Base classes
abstract class AbstractController implements Controller {
    protected $model;
    
    public function __construct($model) {
        $this->model = $model;
    }
    
    public function index() {
        return $this->model->getAll();
    }
    
    public function show($id) {
        return $this->model->find($id);
    }
}

// Validator classes
class EmailValidator implements ValidatorInterface {
    public function validate($data): bool {
        return isset($data['email']) && filter_var($data['email'], FILTER_VALIDATE_EMAIL);
    }
}

class ProductValidator implements ValidatorInterface {
    public function validate($data): bool {
        return isset($data['name']) && isset($data['price']) && $data['price'] > 0;
    }
}

// Concrete controllers
class UserController extends AbstractController implements CreatableController, UpdatableController {
    use LoggableTrait, CachableTrait;
    
    private $validator;
    
    public function __construct($model, ValidatorInterface $validator) {
        parent::__construct($model);
        $this->validator = $validator;
    }
    
    public function create($data) {
        $this->log("Attempting to create user");
        
        if ($this->validator->validate($data)) {
            $result = $this->model->create($data);
            $this->saveToCache('last_created', $result);
            return $result;
        }
        
        $this->log("Validation failed");
        return false;
    }
    
    public function update($id, $data) {
        $this->log("Attempting to update user {$id}");
        
        if ($this->validator->validate($data)) {
            return $this->model->update($id, $data);
        }
        
        $this->log("Validation failed");
        return false;
    }
    
    // New method
    public function authenticate($credentials) {
        // Authentication logic
        return true;
    }
}

// No longer inherits from the same base
class ProductService {
    private $model;
    private $validator;
    
    use CachableTrait;
    
    public function __construct($model, ValidatorInterface $validator) {
        $this->model = $model;
        $this->validator = $validator;
    }
    
    public function getAll() {
        if ($cached = $this->getFromCache('all_products')) {
            return $cached;
        }
        
        $products = $this->model->getAll();
        $this->saveToCache('all_products', $products);
        return $products;
    }
    
    public function getFeatured() {
        return $this->model->getFeatured();
    }
    
    public function addProduct($data) {
        if ($this->validator->validate($data)) {
            return $this->model->create($data);
        }
        return false;
    }
}

// Usage
$userModel = new stdClass(); // Define the models for the after file
$productModel = new stdClass();
$emailValidator = new EmailValidator();
$userController = new UserController($userModel, $emailValidator);

$productValidator = new ProductValidator();
$productService = new ProductService($productModel, $productValidator);
?>
