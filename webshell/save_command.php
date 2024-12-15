<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $command = $_POST['command'];

    $filePath = __DIR__ . '/command.txt';

    if (file_put_contents($filePath, $command) !== false) {
        echo $command + 'Command saved!';
    } else {
        http_response_code(500);
        echo 'Failed to write to file.';
    }
} else {
    http_response_code(405);
    echo 'Method Not Allowed';
}
?>
