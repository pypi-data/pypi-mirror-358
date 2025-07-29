"""
Happy Frog - Arduino Leonardo Device Template

This module provides Arduino code generation specifically for the Arduino Leonardo.
The Leonardo is a classic choice for HID emulation due to its native USB HID support
and widespread availability in the security research community.

Educational Purpose: Demonstrates Arduino-specific code generation and USB HID implementation.

Author: ZeroDumb
License: GNU GPLv3
"""

from typing import List, Dict, Any, Optional
from happy_frog_parser import HappyFrogScript, HappyFrogCommand, CommandType


class ArduinoLeonardoEncoder:
    """
    Encoder that generates Arduino code specifically for Arduino Leonardo.
    
    The Leonardo uses the ATmega32u4 processor and has native USB HID support,
    making it ideal for keyboard and mouse emulation.
    """
    
    def __init__(self):
        """Initialize the Leonardo-specific encoder."""
        self.device_name = "Arduino Leonardo"
        self.processor = "ATmega32u4"
        self.framework = "Arduino"
        
        # Leonardo-specific optimizations
        self.optimizations = {
            'native_usb': True,  # Native USB HID support
            'keyboard_library': True,  # Built-in Keyboard library
            'mouse_library': True,  # Built-in Mouse library
            'serial_debug': True,  # Serial debugging available
        }
    
    def generate_header(self, script: HappyFrogScript) -> List[str]:
        """Generate Leonardo-specific header code."""
        lines = []
        
        lines.append('/*')
        lines.append('Happy Frog - Arduino Leonardo Generated Code')
        lines.append('Educational HID Emulation Script')
        lines.append('')
        lines.append(f'Device: {self.device_name}')
        lines.append(f'Processor: {self.processor}')
        lines.append(f'Framework: {self.framework}')
        lines.append('')
        lines.append('This code was automatically generated from a Happy Frog Script.')
        lines.append('Optimized for Arduino Leonardo with ATmega32u4 processor.')
        lines.append('')
        lines.append('⚠️ IMPORTANT: Use only for educational purposes and authorized testing!')
        lines.append('*/')
        lines.append('')
        
        # Leonardo-specific includes
        lines.append('#include <Keyboard.h>')
        lines.append('#include <Mouse.h>')
        lines.append('')
        
        # Leonardo-specific setup
        lines.append('void setup() {')
        lines.append('  // Initialize Leonardo for HID emulation')
        lines.append('  Keyboard.begin();')
        lines.append('  Mouse.begin();')
        lines.append('  ')
        lines.append('  // Leonardo-specific startup delay')
        lines.append('  delay(2000);  // Wait for system to recognize device')
        lines.append('}')
        lines.append('')
        
        lines.append('void loop() {')
        lines.append('  // Main execution - runs once')
        lines.append('  executePayload();')
        lines.append('  ')
        lines.append('  // Leonardo: Stop execution after payload')
        lines.append('  while(true) {')
        lines.append('    delay(1000);  // Infinite loop to prevent re-execution')
        lines.append('  }')
        lines.append('}')
        lines.append('')
        
        lines.append('void executePayload() {')
        lines.append('  // Generated Happy Frog payload')
        lines.append('')
        
        return lines
    
    def generate_footer(self) -> List[str]:
        """Generate Leonardo-specific footer code."""
        lines = []
        
        lines.append('  // End of Happy Frog payload')
        lines.append('}')
        lines.append('')
        lines.append('/*')
        lines.append('End of Happy Frog Generated Code for Arduino Leonardo')
        lines.append('')
        lines.append('Educational Notes:')
        lines.append('- Arduino Leonardo provides native USB HID support')
        lines.append('- ATmega32u4 processor is optimized for USB communication')
        lines.append('- Built-in Keyboard and Mouse libraries make development easy')
        lines.append('- Classic choice for security research and education')
        lines.append('')
        lines.append('For more information, visit: https://github.com/ZeroDumb/happy-frog')
        lines.append('*/')
        
        return lines
    
    def encode_command(self, command: HappyFrogCommand) -> List[str]:
        """Encode a command specifically for Arduino Leonardo."""
        lines = []
        
        # Add Leonardo-specific comment
        comment = f"  // Leonardo Command: {command.raw_text}"
        lines.append(comment)
        
        # Encode based on command type with Leonardo optimizations
        if command.command_type == CommandType.DELAY:
            lines.extend(self._encode_delay_leonardo(command))
        elif command.command_type == CommandType.STRING:
            lines.extend(self._encode_string_leonardo(command))
        elif command.command_type == CommandType.MODIFIER_COMBO:
            lines.extend(self._encode_modifier_combo_leonardo(command))
        elif command.command_type == CommandType.RANDOM_DELAY:
            lines.extend(self._encode_random_delay_leonardo(command))
        else:
            # Use standard encoding for other commands
            lines.extend(self._encode_standard_command_leonardo(command))
        
        return lines
    
    def _encode_delay_leonardo(self, command: HappyFrogCommand) -> List[str]:
        """Encode delay with Leonardo-specific optimizations."""
        try:
            delay_ms = int(command.parameters[0])
            if delay_ms < 0:
                raise ValueError("Delay value must be non-negative")
            
            return [f"  delay({delay_ms});  // Leonardo delay: {delay_ms}ms"]
                
        except (ValueError, IndexError):
            return ["  // ERROR: Invalid delay value"]
    
    def _encode_string_leonardo(self, command: HappyFrogCommand) -> List[str]:
        """Encode string with Leonardo-specific optimizations."""
        if not command.parameters:
            return ["  // ERROR: STRING command missing text"]
        
        text = command.parameters[0]
        # Arduino Keyboard.print() handles escaping automatically
        return [
            f'  Keyboard.print("{text}");  // Leonardo string input'
        ]
    
    def _encode_modifier_combo_leonardo(self, command: HappyFrogCommand) -> List[str]:
        """Encode modifier combo with Leonardo-specific optimizations."""
        if not command.parameters:
            return ["  // ERROR: MODIFIER_COMBO command missing parameters"]
        
        lines = []
        lines.append("  // Leonardo optimized modifier combo")
        
        # Press all keys in the combo
        for param in command.parameters:
            if param.upper() in ['MOD', 'CTRL', 'SHIFT', 'ALT']:
                key_code = self._get_arduino_keycode(param.upper())
                lines.append(f"  Keyboard.press({key_code});  // Press {param}")
            else:
                key_code = self._get_arduino_keycode(param)
                lines.append(f"  Keyboard.press({key_code});  // Press {param}")
        
        # Release all keys in reverse order
        for param in reversed(command.parameters):
            if param.upper() in ['MOD', 'CTRL', 'SHIFT', 'ALT']:
                key_code = self._get_arduino_keycode(param.upper())
                lines.append(f"  Keyboard.release({key_code});  // Release {param}")
            else:
                key_code = self._get_arduino_keycode(param)
                lines.append(f"  Keyboard.release({key_code});  // Release {param}")
        
        return lines
    
    def _encode_random_delay_leonardo(self, command: HappyFrogCommand) -> List[str]:
        """Encode random delay with Leonardo-specific optimizations."""
        if len(command.parameters) < 2:
            return ["  // ERROR: RANDOM_DELAY command missing min/max values"]
        
        try:
            min_delay = int(command.parameters[0])
            max_delay = int(command.parameters[1])
            
            return [
                f"  // Leonardo optimized random delay: {min_delay}ms to {max_delay}ms",
                "  int random_delay = random(min_delay, max_delay);",
                "  delay(random_delay);"
            ]
            
        except ValueError:
            return ["  // ERROR: Invalid random delay values"]
    
    def _encode_standard_command_leonardo(self, command: HappyFrogCommand) -> List[str]:
        """Encode standard commands for Leonardo."""
        key_code = self._get_arduino_keycode(command.command_type.value)
        return [
            f"  Keyboard.press({key_code});  // Leonardo key press: {command.command_type.value}",
            f"  Keyboard.release({key_code});  // Leonardo key release: {command.command_type.value}"
        ]
    
    def _get_arduino_keycode(self, key: str) -> str:
        """Get Arduino keycode for a key."""
        key = key.upper()
        
        # Modifier keys
        if key == 'MOD':
            return "KEY_LEFT_GUI"
        elif key == 'CTRL':
            return "KEY_LEFT_CTRL"
        elif key == 'SHIFT':
            return "KEY_LEFT_SHIFT"
        elif key == 'ALT':
            return "KEY_LEFT_ALT"
        
        # Single letter keys
        if len(key) == 1 and key.isalpha():
            return f"'{key}'"
        
        # Number keys
        if key.isdigit():
            return f"'{key}'"
        
        # Special mappings
        key_mappings = {
            'ENTER': 'KEY_RETURN',
            'SPACE': "' '",
            'TAB': 'KEY_TAB',
            'BACKSPACE': 'KEY_BACKSPACE',
            'DELETE': 'KEY_DELETE',
            'ESCAPE': 'KEY_ESC',
            'HOME': 'KEY_HOME',
            'END': 'KEY_END',
            'INSERT': 'KEY_INSERT',
            'PAGE_UP': 'KEY_PAGE_UP',
            'PAGE_DOWN': 'KEY_PAGE_DOWN',
            'UP': 'KEY_UP_ARROW',
            'DOWN': 'KEY_DOWN_ARROW',
            'LEFT': 'KEY_LEFT_ARROW',
            'RIGHT': 'KEY_RIGHT_ARROW',
        }
        
        return key_mappings.get(key, f"'{key}'")
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get device information for the Leonardo."""
        return {
            'name': self.device_name,
            'processor': self.processor,
            'framework': self.framework,
            'price_range': '$15-25',
            'difficulty': 'Intermediate',
            'features': [
                'ATmega32u4 processor',
                'Native USB HID support',
                'Built-in Keyboard library',
                'Built-in Mouse library',
                'Serial debugging',
                'Widespread availability',
                'Classic security research choice'
            ],
            'setup_notes': [
                'Install Arduino IDE',
                'Select Arduino Leonardo board',
                'Install Keyboard and Mouse libraries',
                'Upload code to device',
                'Test in controlled environment'
            ]
        } 