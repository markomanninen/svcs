<?php
// After: Code with proper exception handling

class DatabaseException extends Exception {
    public function __construct($message, $code = 0, Exception $previous = null) {
        parent::__construct($message, $code, $previous);
    }
}

class UserNotFoundException extends Exception {
    public function __construct($userId, $code = 0, Exception $previous = null) {
        $message = "User with ID: $userId not found";
        parent::__construct($message, $code, $previous);
    }
}

class Database {
    private $connection;
    
    public function __construct($host, $username, $password, $dbname) {
        try {
            $this->connection = mysqli_connect($host, $username, $password, $dbname);
            
            if (!$this->connection) {
                throw new DatabaseException(mysqli_connect_error(), mysqli_connect_errno());
            }
        } catch (Exception $e) {
            throw new DatabaseException("Failed to connect to database: " . $e->getMessage(), 0, $e);
        }
    }
    
    public function query($sql) {
        try {
            $result = mysqli_query($this->connection, $sql);
            if (!$result) {
                throw new DatabaseException(mysqli_error($this->connection), mysqli_errno($this->connection));
            }
            return $result;
        } catch (Exception $e) {
            throw new DatabaseException("Query failed: " . $e->getMessage(), 0, $e);
        }
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
        try {
            $result = $this->db->query("SELECT * FROM users WHERE id = $id");
            $user = mysqli_fetch_assoc($result);
            
            if (!$user) {
                throw new UserNotFoundException($id);
            }
            
            return $user;
        } catch (UserNotFoundException $e) {
            throw $e;
        } catch (Exception $e) {
            throw new Exception("Error finding user: " . $e->getMessage(), 0, $e);
        }
    }
    
    public function save($user) {
        try {
            $name = $user['name'];
            $email = $user['email'];
            
            $result = $this->db->query("INSERT INTO users (name, email) VALUES ('$name', '$email')");
            return true;
        } catch (Exception $e) {
            throw new Exception("Error saving user: " . $e->getMessage(), 0, $e);
        }
    }
}

// Usage
function getUserData($userId) {
    try {
        $db = new Database('localhost', 'root', 'password', 'app');
        $userRepo = new UserRepository($db);
        
        return $userRepo->findById($userId);
    } catch (UserNotFoundException $e) {
        return ['error' => $e->getMessage()];
    } catch (DatabaseException $e) {
        error_log("Database error: " . $e->getMessage());
        return ['error' => 'Database error occurred'];
    } catch (Exception $e) {
        error_log("Unexpected error: " . $e->getMessage());
        return ['error' => 'An unexpected error occurred'];
    } finally {
        if (isset($db)) {
            $db->close();
        }
    }
}

function createUser($userData) {
    try {
        $db = new Database('localhost', 'root', 'password', 'app');
        $userRepo = new UserRepository($db);
        
        $userRepo->save($userData);
        return ['success' => true];
    } catch (DatabaseException $e) {
        error_log("Database error: " . $e->getMessage());
        return ['error' => 'Database error occurred'];
    } catch (Exception $e) {
        error_log("Error creating user: " . $e->getMessage());
        return ['error' => 'Failed to create user'];
    } finally {
        if (isset($db)) {
            $db->close();
        }
    }
}
?>
