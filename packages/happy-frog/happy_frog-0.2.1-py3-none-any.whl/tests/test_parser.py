"""
Tests for the Happy Frog Script parser.

Educational Purpose: This demonstrates unit testing practices,
including test case design, edge case handling, and validation testing.
"""

import pytest
import tempfile
import os
from happy_frog_parser import HappyFrogParser, HappyFrogScript, HappyFrogCommand, CommandType, HappyFrogScriptError


class TestHappyFrogParser:
    """Test cases for the Happy Frog Script parser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = HappyFrogParser()
    
    def test_parse_simple_commands(self):
        """Test parsing of simple commands without parameters."""
        script_content = """
DELAY 1000
STRING Hello World
ENTER
SPACE
TAB
"""
        script = self.parser.parse_string(script_content)
        
        assert len(script.commands) == 5
        assert script.commands[0].command_type == CommandType.DELAY
        assert script.commands[0].parameters == ['1000']
        assert script.commands[1].command_type == CommandType.STRING
        assert script.commands[1].parameters == ['Hello World']
        assert script.commands[2].command_type == CommandType.ENTER
        assert script.commands[3].command_type == CommandType.SPACE
        assert script.commands[4].command_type == CommandType.TAB
    
    def test_parse_modifier_keys(self):
        """Test parsing of modifier keys including MOD."""
        script_content = """
CTRL
SHIFT
ALT
MOD
"""
        script = self.parser.parse_string(script_content)
        
        assert len(script.commands) == 4
        assert script.commands[0].command_type == CommandType.CTRL
        assert script.commands[1].command_type == CommandType.SHIFT
        assert script.commands[2].command_type == CommandType.ALT
        assert script.commands[3].command_type == CommandType.MOD
    
    def test_parse_modifier_combos(self):
        """Test parsing of modifier+key combinations."""
        script_content = """
MOD r
CTRL ALT DEL
SHIFT F1
"""
        script = self.parser.parse_string(script_content)
        
        assert len(script.commands) == 3
        assert script.commands[0].command_type == CommandType.MODIFIER_COMBO
        assert script.commands[0].parameters == ['MOD', 'r']
        assert script.commands[1].command_type == CommandType.MODIFIER_COMBO
        assert script.commands[1].parameters == ['CTRL', 'ALT', 'DEL']
        assert script.commands[2].command_type == CommandType.MODIFIER_COMBO
        assert script.commands[2].parameters == ['SHIFT', 'F1']
    
    def test_parse_comments(self):
        """Test parsing of comment lines."""
        script_content = """
# This is a comment
REM This is also a comment
STRING Hello
# Another comment
"""
        script = self.parser.parse_string(script_content)
        
        assert len(script.commands) == 4
        assert script.commands[0].command_type == CommandType.COMMENT
        assert script.commands[0].parameters == [' This is a comment']
        assert script.commands[1].command_type == CommandType.REM
        assert script.commands[1].parameters == ['This is also a comment']
        assert script.commands[2].command_type == CommandType.STRING
        assert script.commands[3].command_type == CommandType.COMMENT
    
    def test_parse_empty_comments(self):
        """Test parsing of empty comment lines."""
        script_content = """
#
REM
STRING Hello
"""
        script = self.parser.parse_string(script_content)
        
        assert len(script.commands) == 3
        assert script.commands[0].command_type == CommandType.COMMENT
        assert script.commands[0].parameters == ['']  # Empty comment
        assert script.commands[1].command_type == CommandType.REM
        assert script.commands[1].parameters == ['']  # Empty REM
        assert script.commands[2].command_type == CommandType.STRING
    
    def test_parse_delay_validation(self):
        """Test delay command validation."""
        # Valid delay
        script_content = "DELAY 1000"
        script = self.parser.parse_string(script_content)
        assert script.commands[0].parameters == ['1000']
        
        # Invalid delay (should still parse but fail validation)
        script_content = "DELAY invalid"
        script = self.parser.parse_string(script_content)
        assert script.commands[0].parameters == ['invalid']
    
    def test_parse_unknown_command(self):
        """Test handling of unknown commands."""
        script_content = "UNKNOWN_COMMAND"
        
        with pytest.raises(HappyFrogScriptError) as exc_info:
            self.parser.parse_string(script_content)
        
        assert "Unknown command" in str(exc_info.value)
    
    def test_parse_file(self):
        """Test parsing from a file."""
        script_content = """
DELAY 1000
STRING Test from file
ENTER
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(script_content)
            temp_file = f.name
        
        try:
            script = self.parser.parse_file(temp_file)
            assert len(script.commands) == 3
            assert script.metadata['source'] == temp_file
        finally:
            os.unlink(temp_file)
    
    def test_parse_file_not_found(self):
        """Test handling of non-existent files."""
        with pytest.raises(HappyFrogScriptError) as exc_info:
            self.parser.parse_file("nonexistent_file.txt")
        
        assert "File not found" in str(exc_info.value)
    
    def test_parse_empty_file(self):
        """Test parsing of empty files."""
        script = self.parser.parse_string("")
        assert len(script.commands) == 0
        assert script.metadata['total_commands'] == 0
    
    def test_parse_whitespace_only(self):
        """Test parsing of files with only whitespace."""
        script = self.parser.parse_string("   \n\t\n  ")
        assert len(script.commands) == 0
    
    def test_line_numbers(self):
        """Test that line numbers are correctly assigned."""
        script_content = """
# Comment on line 2
DELAY 1000
STRING Hello
# Comment on line 5
ENTER
"""
        script = self.parser.parse_string(script_content)
        
        assert script.commands[0].line_number == 2  # Comment
        assert script.commands[1].line_number == 3  # DELAY
        assert script.commands[2].line_number == 4  # STRING
        assert script.commands[3].line_number == 5  # Comment
        assert script.commands[4].line_number == 6  # ENTER
    
    def test_metadata(self):
        """Test that metadata is correctly populated."""
        script_content = "DELAY 1000\nSTRING Hello"
        script = self.parser.parse_string(script_content, "test_source")
        
        assert script.metadata['source'] == "test_source"
        assert script.metadata['total_commands'] == 2
        assert script.metadata['total_lines'] == 2
    
    def test_validate_script(self):
        """Test script validation."""
        # Valid script
        script_content = "DELAY 1000\nSTRING Hello"
        script = self.parser.parse_string(script_content)
        warnings = self.parser.validate_script(script)
        assert len(warnings) == 0
        
        # Script with very long delay
        script_content = "DELAY 120000"  # 2 minutes
        script = self.parser.parse_string(script_content)
        warnings = self.parser.validate_script(script)
        assert len(warnings) == 1
        assert "Very long delay" in warnings[0]
        
        # Empty script
        script = self.parser.parse_string("")
        warnings = self.parser.validate_script(script)
        assert len(warnings) == 1
        assert "contains no commands" in warnings[0]
    
    def test_case_insensitive_commands(self):
        """Test that commands are case-insensitive."""
        script_content = """
delay 1000
string Hello
enter
mod r
"""
        script = self.parser.parse_string(script_content)
        
        assert script.commands[0].command_type == CommandType.DELAY
        assert script.commands[1].command_type == CommandType.STRING
        assert script.commands[2].command_type == CommandType.ENTER
        assert script.commands[3].command_type == CommandType.MODIFIER_COMBO
        assert script.commands[3].parameters == ['mod', 'r']


if __name__ == "__main__":
    pytest.main([__file__]) 