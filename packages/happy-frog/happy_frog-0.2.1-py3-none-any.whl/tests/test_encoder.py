"""
Tests for the Happy Frog Script encoder.

Educational Purpose: This demonstrates testing of code generation,
including output validation, edge case handling, and integration testing.
"""

import pytest
import tempfile
import os
from happy_frog_parser import (
    HappyFrogParser, 
    CircuitPythonEncoder, 
    HappyFrogScript, 
    HappyFrogCommand, 
    CommandType,
    HappyFrogScriptError,
    EncoderError
)


class TestCircuitPythonEncoder:
    """Test cases for the CircuitPython encoder."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.encoder = CircuitPythonEncoder()
        self.parser = HappyFrogParser()
    
    def test_encoder_initialization(self):
        """Test that the encoder initializes correctly."""
        assert self.encoder is not None
        assert hasattr(self.encoder, 'key_codes')
        assert hasattr(self.encoder, 'templates')
        assert len(self.encoder.key_codes) > 0
    
    def test_encode_simple_script(self):
        """Test encoding a simple script with basic commands."""
        script_content = """
DELAY 1000
STRING Hello World
ENTER
"""
        script = self.parser.parse_string(script_content)
        code = self.encoder.encode(script)
        
        # Check that the code contains expected elements
        assert "import time" in code
        assert "import usb_hid" in code
        assert "from adafruit_hid.keyboard import Keyboard" in code
        assert "time.sleep(1.0)" in code  # 1000ms = 1.0s
        assert 'keyboard_layout.write("Hello World")' in code
        assert "keyboard.press(Keycode.ENTER)" in code
    
    def test_encode_modifier_keys(self):
        """Test encoding of modifier keys including MOD."""
        script_content = """
CTRL
SHIFT
ALT
MOD
"""
        script = self.parser.parse_string(script_content)
        code = self.encoder.encode(script)
        
        assert "keyboard.press(Keycode.CONTROL)" in code
        assert "keyboard.press(Keycode.SHIFT)" in code
        assert "keyboard.press(Keycode.ALT)" in code
        assert "keyboard.press(Keycode.GUI)" in code  # MOD maps to GUI
        assert "keyboard.release(Keycode.CONTROL)" in code
        assert "keyboard.release(Keycode.SHIFT)" in code
        assert "keyboard.release(Keycode.ALT)" in code
        assert "keyboard.release(Keycode.GUI)" in code
    
    def test_encode_modifier_combos(self):
        """Test encoding of modifier+key combinations."""
        script_content = """
MOD r
CTRL ALT DEL
SHIFT F1
"""
        script = self.parser.parse_string(script_content)
        code = self.encoder.encode(script)
        
        # Check that MOD r generates the correct code
        assert "keyboard.press(Keycode.GUI)" in code  # MOD maps to GUI
        assert "keyboard.press(Keycode.R)" in code
        assert "keyboard.release(Keycode.R)" in code
        assert "keyboard.release(Keycode.GUI)" in code
        
        # Check that CTRL ALT DEL generates the correct code
        assert "keyboard.press(Keycode.CONTROL)" in code
        assert "keyboard.press(Keycode.ALT)" in code
        assert "keyboard.press(Keycode.DELETE)" in code
        assert "keyboard.release(Keycode.DELETE)" in code
        assert "keyboard.release(Keycode.ALT)" in code
        assert "keyboard.release(Keycode.CONTROL)" in code
        
        # Check that SHIFT F1 generates the correct code
        assert "keyboard.press(Keycode.SHIFT)" in code
        assert "keyboard.press(Keycode.F1)" in code
        assert "keyboard.release(Keycode.F1)" in code
        assert "keyboard.release(Keycode.SHIFT)" in code
    
    def test_encode_comments(self):
        """Test encoding of comment commands."""
        script_content = """
# This is a comment
STRING Hello
REM This is also a comment
"""
        script = self.parser.parse_string(script_content)
        code = self.encoder.encode(script)
        
        assert "# This is a comment" in code
        assert "# This is also a comment" in code
        assert 'keyboard_layout.write("Hello")' in code
    
    def test_encode_special_keys(self):
        """Test encoding of special key commands."""
        script_content = """
SPACE
TAB
BACKSPACE
DELETE
UP
DOWN
LEFT
RIGHT
HOME
END
INSERT
PAGE_UP
PAGE_DOWN
ESCAPE
"""
        script = self.parser.parse_string(script_content)
        code = self.encoder.encode(script)
        
        # Check that all special keys are encoded correctly
        special_keys = [
            "SPACE", "TAB", "BACKSPACE", "DELETE",
            "UP_ARROW", "DOWN_ARROW", "LEFT_ARROW", "RIGHT_ARROW",
            "HOME", "END", "INSERT", "PAGE_UP", "PAGE_DOWN", "ESCAPE"
        ]
        
        for key in special_keys:
            assert f"Keycode.{key}" in code
    
    def test_encode_function_keys(self):
        """Test encoding of function key commands."""
        script_content = "F1\nF2\nF3\nF4\nF5\nF6\nF7\nF8\nF9\nF10\nF11\nF12"
        script = self.parser.parse_string(script_content)
        code = self.encoder.encode(script)
        
        # Check that all function keys are encoded correctly
        for i in range(1, 13):
            assert f"Keycode.F{i}" in code
    
    def test_encode_delay_validation(self):
        """Test encoding of delay commands with validation."""
        # Valid delay
        script_content = "DELAY 1000"
        script = self.parser.parse_string(script_content)
        code = self.encoder.encode(script)
        assert "time.sleep(1.0)" in code
        
        # Invalid delay should raise an error during encoding
        script_content = "DELAY invalid"
        script = self.parser.parse_string(script_content)
        
        with pytest.raises(EncoderError) as exc_info:
            self.encoder.encode(script)
        
        assert "Invalid delay value" in str(exc_info.value)
    
    def test_encode_string_escaping(self):
        """Test that strings are properly escaped in the output."""
        script_content = 'STRING Hello "World" with \'quotes\' and \\backslashes\\'
        script = self.parser.parse_string(script_content)
        code = self.encoder.encode(script)
        
        # Check that quotes are escaped
        assert 'keyboard_layout.write("Hello \\"World\\" with \'quotes\' and \\\\backslashes\\\\")' in code
    
    def test_encode_to_file(self):
        """Test encoding to a file."""
        script_content = "DELAY 1000\nSTRING Test\nENTER"
        script = self.parser.parse_string(script_content)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            temp_file = f.name
        
        try:
            code = self.encoder.encode(script, temp_file)
            
            # Check that the file was created and contains the code
            assert os.path.exists(temp_file)
            with open(temp_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            assert file_content == code
            assert "time.sleep(1.0)" in file_content
            assert 'keyboard_layout.write("Test")' in file_content
            assert "keyboard.press(Keycode.ENTER)" in file_content
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_encode_metadata_in_header(self):
        """Test that script metadata is included in the generated header."""
        script_content = "DELAY 1000\nSTRING Hello"
        script = self.parser.parse_string(script_content, "test_script.txt")
        code = self.encoder.encode(script)
        
        # Check that metadata is included in comments
        assert "# Source: test_script.txt" in code
        assert "# Total Commands: 2" in code
        assert "# Total Lines: 2" in code
    
    def test_encode_empty_script(self):
        """Test encoding an empty script."""
        script = self.parser.parse_string("")
        code = self.encoder.encode(script)
        
        # Should still generate valid CircuitPython code
        assert "import time" in code
        assert "import usb_hid" in code
        assert "def main():" in code
        assert "if __name__ == '__main__':" in code
    
    def test_encode_whitespace_only_script(self):
        """Test encoding a script with only whitespace."""
        script = self.parser.parse_string("   \n\t\n  ")
        code = self.encoder.encode(script)
        
        # Should still generate valid CircuitPython code
        assert "import time" in code
        assert "def main():" in code
    
    def test_validate_script(self):
        """Test script validation in the encoder."""
        # Valid script
        script_content = "DELAY 1000\nSTRING Hello"
        script = self.parser.parse_string(script_content)
        warnings = self.encoder.validate_script(script)
        assert len(warnings) == 0
        
        # Script with very long string
        long_string = "A" * 1500  # 1500 characters
        script_content = f"STRING {long_string}"
        script = self.parser.parse_string(script_content)
        warnings = self.encoder.validate_script(script)
        assert len(warnings) == 1
        assert "Very long string" in warnings[0]
        
        # Script with unsupported command (should be handled gracefully)
        # Note: This would require adding an unsupported command type for testing
    
    def test_key_mapping(self):
        """Test the key mapping functionality."""
        # Test single letter keys
        assert self.encoder._map_key_to_keycode('a') == 'Keycode.A'
        assert self.encoder._map_key_to_keycode('Z') == 'Keycode.Z'
        
        # Test number keys
        assert self.encoder._map_key_to_keycode('1') == 'Keycode.1'
        assert self.encoder._map_key_to_keycode('9') == 'Keycode.9'
        
        # Test special mappings
        assert self.encoder._map_key_to_keycode('DEL') == 'Keycode.DELETE'
        assert self.encoder._map_key_to_keycode('ESC') == 'Keycode.ESCAPE'
        assert self.encoder._map_key_to_keycode('ENTER') == 'Keycode.ENTER'
        
        # Test fallback for unknown keys
        assert self.encoder._map_key_to_keycode('UNKNOWN') == 'Keycode.UNKNOWN'
    
    def test_encode_complex_script(self):
        """Test encoding a complex script with multiple command types."""
        script_content = """
# Complex script test
DELAY 2000
MOD r
DELAY 500
STRING notepad
ENTER
DELAY 1000
STRING This is a test of Happy Frog Script!
CTRL s
DELAY 500
STRING test.txt
ENTER
DELAY 500
ALT F4
"""
        script = self.parser.parse_string(script_content)
        code = self.encoder.encode(script)
        
        # Check that all expected elements are present
        assert "time.sleep(2.0)" in code  # 2000ms
        assert "keyboard.press(Keycode.GUI)" in code  # MOD
        assert "keyboard.press(Keycode.R)" in code
        assert 'keyboard_layout.write("notepad")' in code
        assert 'keyboard_layout.write("This is a test of Happy Frog Script!")' in code
        assert "keyboard.press(Keycode.CONTROL)" in code
        assert "keyboard.press(Keycode.S)" in code
        assert 'keyboard_layout.write("test.txt")' in code
        assert "keyboard.press(Keycode.ALT)" in code
        assert "keyboard.press(Keycode.F4)" in code
    
    def test_encode_error_handling(self):
        """Test error handling during encoding."""
        # Test with invalid delay
        script_content = "DELAY invalid"
        script = self.parser.parse_string(script_content)
        
        with pytest.raises(EncoderError) as exc_info:
            self.encoder.encode(script)
        
        assert "Invalid delay value" in str(exc_info.value)
        
        # Test with missing parameters in MODIFIER_COMBO
        # This would require creating a command with missing parameters
        # which is difficult to do through the parser, so we'll test the
        # encoder's internal error handling differently
    
    def test_template_generation(self):
        """Test that templates are generated correctly."""
        # Test header template
        header = self.encoder._get_header_template()
        assert "Happy Frog - Generated CircuitPython Code" in header
        assert "import time" in header
        assert "import usb_hid" in header
        
        # Test footer template
        footer = self.encoder._get_footer_template()
        assert "End of Happy Frog Generated Code" in footer
        assert "Educational Notes:" in footer


if __name__ == "__main__":
    pytest.main([__file__]) 