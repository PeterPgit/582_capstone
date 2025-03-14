<?php
$password = "deepracer";
$hashedpassword = password_hash($password, PASSWORD_BCRYPT);
echo "Hashed Password: ". $hashedpassword;
echo "\n";
?>
