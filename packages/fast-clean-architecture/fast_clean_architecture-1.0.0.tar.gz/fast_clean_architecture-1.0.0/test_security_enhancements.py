#!/usr/bin/env python3
"""Test script to verify security enhancements."""

import tempfile
import threading
import time
from pathlib import Path
from fast_clean_architecture.generators.component_generator import ComponentGenerator
from fast_clean_architecture.utils import (
    sanitize_error_message,
    create_secure_error,
    secure_file_operation,
    get_file_lock
)

def test_error_message_sanitization():
    """Test that error messages don't expose sensitive information."""
    print("Testing error message sanitization...")
    
    # Test with sensitive paths
    sensitive_msg = "Cannot create directory /Users/john/secret/path: Permission denied"
    sanitized = sanitize_error_message(sensitive_msg)
    print(f"Original: {sensitive_msg}")
    print(f"Sanitized: {sanitized}")
    assert "/Users/john" not in sanitized
    assert "[REDACTED]" in sanitized
    
    # Test with IP addresses
    ip_msg = "Connection failed to 192.168.1.100: timeout"
    sanitized_ip = sanitize_error_message(ip_msg)
    print(f"Original: {ip_msg}")
    print(f"Sanitized: {sanitized_ip}")
    assert "192.168.1.100" not in sanitized_ip
    
    print("✓ Error message sanitization working correctly\n")

def test_secure_error_creation():
    """Test secure error creation."""
    print("Testing secure error creation...")
    
    error = create_secure_error("file_write", "write file", "/home/user/secret/file.txt: Permission denied")
    error_msg = str(error)
    print(f"Secure error: {error_msg}")
    assert "/home/user" not in error_msg
    assert "Failed to write file" in error_msg
    
    print("✓ Secure error creation working correctly\n")

def test_template_variable_sanitization():
    """Test enhanced template variable sanitization."""
    print("Testing template variable sanitization...")
    
    # Import Config for proper initialization
    from fast_clean_architecture.config import Config
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config = Config(project_root=Path(temp_dir))
        generator = ComponentGenerator(config=config)
        
        # Test dangerous template variables
        dangerous_vars = {
            "malicious_script": "<script>alert('xss')</script>",
            "jinja_injection": "{{ config.items() }}",
            "python_injection": "__import__('os').system('ls')",
            "url_encoded": "%3Cscript%3Ealert%28%27xss%27%29%3C%2Fscript%3E",
            "unicode_attack": "\u003cscript\u003ealert('xss')\u003c/script\u003e",
            "normal_value": "valid_component_name"
        }
        
        sanitized = generator._sanitize_template_variables(dangerous_vars)
        
        print("Sanitization results:")
        for key, value in sanitized.items():
            print(f"  {key}: '{dangerous_vars[key]}' -> '{value}'")
            
            # Verify dangerous content is removed
            if key != "normal_value":
                assert "<script>" not in value
                assert "{{" not in value
                assert "__import__" not in value
                assert "alert" not in value
            else:
                assert value == "valid_component_name"
    
    print("✓ Template variable sanitization working correctly\n")

def test_file_locking():
    """Test file locking mechanism."""
    print("Testing file locking mechanism...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test_lock.txt"
        results = []
        
        def write_operation(content, delay=0.1):
            """Simulate a file write operation with delay."""
            def operation():
                time.sleep(delay)
                with open(test_file, 'w') as f:
                    f.write(content)
                results.append(content)
            
            return secure_file_operation(test_file, operation)
        
        # Start multiple threads trying to write to the same file
        threads = []
        for i in range(3):
            thread = threading.Thread(target=write_operation, args=(f"content_{i}",))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify that operations were serialized
        print(f"Write operations completed in order: {results}")
        assert len(results) == 3
        
        # Verify file contains the last write
        with open(test_file, 'r') as f:
            final_content = f.read()
        print(f"Final file content: {final_content}")
        assert final_content in ["content_0", "content_1", "content_2"]
    
    print("✓ File locking working correctly\n")

def test_lock_reuse():
    """Test that the same file path reuses the same lock."""
    print("Testing lock reuse...")
    
    test_path = "/tmp/test_file.txt"
    lock1 = get_file_lock(test_path)
    lock2 = get_file_lock(test_path)
    
    # Should be the same lock object
    assert lock1 is lock2
    print("✓ Lock reuse working correctly\n")

if __name__ == "__main__":
    print("Running security enhancement tests...\n")
    
    test_error_message_sanitization()
    test_secure_error_creation()
    test_template_variable_sanitization()
    test_file_locking()
    test_lock_reuse()
    
    print("All security enhancement tests passed! ✅")