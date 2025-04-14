<!-- 
Authors: Ian Wilson, Andrew Uriell, Peter Pharm, Michael Oliver 
Class: Senior Design -- EECS582
Date: March 26, 2025
Purpose: Runs the login page for the website and connects to the database
Code sources: Stackoverflow, ChatGPT, ourselves 
-->

<?php
session_start();

// Database connection settings
$servername = "localhost"; 
$username = "deepracer_user";
$password = "YourStrongPassword";
$dbname = "deepracer_db"; 

// Enable error reporting (for debugging, remove in production)
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Connect to MySQL
$conn = new mysqli($servername, $username, $password, $dbname);

// Check if connection was successful
if ($conn->connect_error) {
    die(json_encode(["status" => "error", "message" => "Database connection failed: " . $conn->connect_error]));
}

// Get JSON input from the request
$data = json_decode(file_get_contents("php://input"), true);
$user = $data["username"] ?? '';
$pass = $data["password"] ?? '';

// Prevent empty input
if (empty($user) || empty($pass)) {
    die(json_encode(["status" => "error", "message" => "Username and password are required"]));
}

// Prepare statement to prevent SQL injection
$stmt = $conn->prepare("SELECT password_hash FROM users WHERE username = ?");
$stmt->bind_param("s", $user);
$stmt->execute();
$stmt->bind_result($password_hash);
$stmt->fetch();
$stmt->close();

// Verify password if user exists
if ($password_hash && password_verify($pass, $password_hash)) {
    $_SESSION["loggedin"] = true;
    $_SESSION["username"] = $user;
    echo json_encode(["status" => "success", "message" => "Login successful"]);
} else {
    echo json_encode(["status" => "error", "message" => "Invalid credentials"]);
}

// Close database connection
$conn->close();
?>

