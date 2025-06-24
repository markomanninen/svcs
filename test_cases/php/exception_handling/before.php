<?php
// Before: Code without proper exception handling

class Database {
    private $connection;
    
    public function __construct($host, $username, $password, $dbname) {
        $this->connection = mysqli_connect($host, $username, $password, $dbname);
        
        if (!$this->connection) {
            return false;
        }
    }
    
    public function query($sql) {
        $result = mysqli_query($this->connection, $sql);
        if (!$result) {
            return false;
        }
        return $result;
    }
    
    public function close() {
        mysqli_close($this->connection);
    }
}

class UserRepository {
    private $db;
    
    public function __construct($db) {
        $this->db = $db;
    }
    
    public function findById($id) {
        $result = $this->db->query("SELECT * FROM users WHERE id = $id");
        if (!$result) {
            return null;
        }
        
        return mysqli_fetch_assoc($result);
    }
    
    public function save($user) {
        $name = $user['name'];
        $email = $user['email'];
        
        $result = $this->db->query("INSERT INTO users (name, email) VALUES ('$name', '$email')");
        if (!$result) {
            return false;
        }
        
        return true;
    }
}

// Usage
function getUserData($userId) {
    $db = new Database('localhost', 'root', 'password', 'app');
    $userRepo = new UserRepository($db);
    
    $user = $userRepo->findById($userId);
    if (!$user) {
        return ['error' => 'User not found'];
    }
    
    return $user;
}

function createUser($userData) {
    $db = new Database('localhost', 'root', 'password', 'app');
    $userRepo = new UserRepository($db);
    
    $result = $userRepo->save($userData);
    if (!$result) {
        return ['error' => 'Failed to create user'];
    }
    
    return ['success' => true];
}
?>
