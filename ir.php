<?php
// IR Sensor Detection Endpoint with Error Logging
// Returns JSON with detection status and error details for debugging

header('Content-Type: application/json');

try {
    // Find the Python script
    $scriptPath = __DIR__ . '/read_ir_sensor.py';
    
    // Check if file exists
    if (!file_exists($scriptPath)) {
        throw new Exception('read_ir_sensor.py not found');
    }
    
    // Run with SUDO (critical for GPIO access)
    $command = "sudo python3 {$scriptPath} 2>&1";
    $output = shell_exec($command);
    $output = trim($output);
    
    error_log("Command: " . $command);
    error_log("Output: " . $output);
    
    // Parse JSON
    $data = json_decode($output, true);
    
    if ($data === null) {
        throw new Exception('Invalid JSON response: ' . $output);
    }
    
    if (isset($data['error'])) {
        throw new Exception($data['error']);
    }
    
    if (isset($data['detected']) && $data['detected'] === true) {
        if (empty($data['verification_token'])) {
            $data['verification_token'] = bin2hex(random_bytes(16));
        }
    }
    
    echo json_encode($data);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'detected' => false,
        'error' => $e->getMessage()
    ]);
}
?>
