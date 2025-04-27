<!-- 
Authors: Ian Wilson, Andrew Uriell, Peter Pham, Michael Oliver, Jack Youngquist
Class: Senior Design -- EECS582
Date: March 13, 2025
Purpose: Hashes password
Code sources: Stackoverflow, ChatGPT, ourselves 
-->
<?php
$password = "deepracer";
$hashedpassword = password_hash($password, PASSWORD_BCRYPT);
echo "Hashed Password: ". $hashedpassword;
echo "\n";
?>
