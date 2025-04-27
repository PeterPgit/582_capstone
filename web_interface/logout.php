<!-- 
Authors: Ian Wilson, Andrew Uriell, Peter Pham, Michael Oliver, Jack Youngquist
Class: Senior Design -- EECS582
Date: March 13, 2025
Purpose: Handles log out and ending sessions
Code sources: Stackoverflow, ChatGPT, ourselves 
-->
<?php
session_start();
session_destroy();
echo json_encode(["status" => "success", "message" => "Logged out successfully"]);
?>
