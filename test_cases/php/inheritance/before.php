<?php
// Before: Simple inheritance structure

class BaseController {
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
    
    protected function validate($data) {
        // Base validation
        return true;
    }
}

class UserController extends BaseController {
    public function create($data) {
        if ($this->validate($data)) {
            return $this->model->create($data);
        }
        return false;
    }
    
    public function update($id, $data) {
        if ($this->validate($data)) {
            return $this->model->update($id, $data);
        }
        return false;
    }
    
    protected function validate($data) {
        // Override parent validate
        if (!isset($data['email'])) {
            return false;
        }
        return parent::validate($data);
    }
}

class ProductController extends BaseController {
    public function featured() {
        return $this->model->getFeatured();
    }
}

// Usage
$userModel = new stdClass(); // Define the models for the before file
$productModel = new stdClass();
$userController = new UserController($userModel);
$productController = new ProductController($productModel);
?>
