"""
Happy Frog - Teensy 4.0 Device Template

This module provides Arduino code generation specifically for the Teensy 4.0.
The Teensy 4.0 is a high-performance device popular in advanced security research
due to its ARM Cortex-M7 processor and extensive USB HID capabilities.

Educational Purpose: Demonstrates high-performance device optimization and advanced features.

Author: ZeroDumb
License: GNU GPLv3
"""

from typing import List, Dict, Any, Optional
from happy_frog_parser import HappyFrogScript, HappyFrogCommand, CommandType


class Teensy4Encoder:
    """
    Encoder that generates Arduino code specifically for Teensy 4.0.
    
    The Teensy 4.0 uses the ARM Cortex-M7 processor and provides excellent
    performance for complex HID emulation scenarios.
    """
    
    def __init__(self):
        """Initialize the Teensy 4.0-specific encoder."""
        self.device_name = "Teensy 4.0"
        self.processor = "ARM Cortex-M7"
        self.framework = "Arduino (Teensyduino)"
        
        # Teensy 4.0-specific optimizations
        self.optimizations = {
            'high_performance': True,  # 600MHz processor
            'extended_usb': True,  # Extended USB HID support
            'flash_storage': True,  # Large flash storage
            'sram_optimized': True,  # 1MB SRAM
            'crypto_hardware': True,  # Hardware crypto acceleration
        }
    
    def generate_header(self, script: HappyFrogScript) -> List[str]:
        """Generate Teensy 4.0-specific header code."""
        lines = []
        
        lines.append('/*')
        lines.append('Happy Frog - Teensy 4.0 Generated Code')
        lines.append('Educational HID Emulation Script')
        lines.append('')
        lines.append(f'Device: {self.device_name}')
        lines.append(f'Processor: {self.processor}')
        lines.append(f'Framework: {self.framework}')
        lines.append('')
        lines.append('This code was automatically generated from a Happy Frog Script.')
        lines.append('Optimized for Teensy 4.0 with ARM Cortex-M7 processor.')
        lines.append('')
        lines.append('⚠️ IMPORTANT: Use only for educational purposes and authorized testing!')
        lines.append('*/')
        lines.append('')
        
        # Teensy 4.0-specific includes
        lines.append('#include <Keyboard.h>')
        lines.append('#include <Mouse.h>')
        lines.append('#include <USBHost_t36.h>  // Teensy 4.0 USB Host support')
        lines.append('')
        
        # Teensy 4.0-specific setup
        lines.append('void setup() {')
        lines.append('  // Initialize Teensy 4.0 for high-performance HID emulation')
        lines.append('  Keyboard.begin();')
        lines.append('  Mouse.begin();')
        lines.append('  ')
        lines.append('  // Teensy 4.0: Fast startup with minimal delay')
        lines.append('  delay(500);  // Optimized startup delay')
        lines.append('}')
        lines.append('')
        
        lines.append('void loop() {')
        lines.append('  // Main execution - runs once')
        lines.append('  executePayload();')
        lines.append('  ')
        lines.append('  // Teensy 4.0: Efficient infinite loop')
        lines.append('  while(true) {')
        lines.append('    yield();  // Allow background tasks')
        lines.append('  }')
        lines.append('}')
        lines.append('')
        
        lines.append('void executePayload() {')
        lines.append('  // Generated Happy Frog payload for Teensy 4.0')
        lines.append('')
        
        return lines
    
    def generate_footer(self) -> List[str]:
        """Generate Teensy 4.0-specific footer code."""
        lines = []
        
        lines.append('  // End of Happy Frog payload')
        lines.append('}')
        lines.append('')
        lines.append('/*')
        lines.append('End of Happy Frog Generated Code for Teensy 4.0')
        lines.append('')
        lines.append('Educational Notes:')
        lines.append('- Teensy 4.0 provides exceptional performance for HID emulation')
        lines.append('- ARM Cortex-M7 processor enables complex automation scenarios')
        lines.append('- Extended USB capabilities support advanced HID features')
        lines.append('- Hardware crypto acceleration available for advanced applications')
        lines.append('')
        lines.append('For more information, visit: https://github.com/ZeroDumb/happy-frog')
        lines.append('*/')
        
        return lines
    
    def encode_command(self, command: HappyFrogCommand) -> List[str]:
        """Encode a command specifically for Teensy 4.0."""
        lines = []
        
        # Add Teensy 4.0-specific comment
        comment = f"  // Teensy 4.0 Command: {command.raw_text}"
        lines.append(comment)
        
        # Encode based on command type with Teensy 4.0 optimizations
        if command.command_type == CommandType.DELAY:
            lines.extend(self._encode_delay_teensy(command))
        elif command.command_type == CommandType.STRING:
            lines.extend(self._encode_string_teensy(command))
        elif command.command_type == CommandType.MODIFIER_COMBO:
            lines.extend(self._encode_modifier_combo_teensy(command))
        elif command.command_type == CommandType.RANDOM_DELAY:
            lines.extend(self._encode_random_delay_teensy(command))
        else:
            # Use standard encoding for other commands
            lines.extend(self._encode_standard_command_teensy(command))
        
        return lines
    
    def _encode_delay_teensy(self, command: HappyFrogCommand) -> List[str]:
        """Encode delay with Teensy 4.0-specific optimizations."""
        try:
            delay_ms = int(command.parameters[0])
            if delay_ms < 0:
                raise ValueError("Delay value must be non-negative")
            
            # Teensy 4.0: High-precision delays
            if delay_ms < 1:
                return [f"  delayMicroseconds({delay_ms * 1000});  // Teensy 4.0 microsecond delay"]
            else:
                return [f"  delay({delay_ms});  // Teensy 4.0 optimized delay: {delay_ms}ms"]
                
        except (ValueError, IndexError):
            return ["  // ERROR: Invalid delay value"]
    
    def _encode_string_teensy(self, command: HappyFrogCommand) -> List[str]:
        """Encode string with Teensy 4.0-specific optimizations."""
        if not command.parameters:
            return ["  // ERROR: STRING command missing text"]
        
        text = command.parameters[0]
        # Teensy 4.0: High-performance string input
        return [
            f'  Keyboard.print("{text}");  // Teensy 4.0 high-performance string input'
        ]
    
    def _encode_modifier_combo_teensy(self, command: HappyFrogCommand) -> List[str]:
        """Encode modifier combo with Teensy 4.0-specific optimizations."""
        if not command.parameters:
            return ["  // ERROR: MODIFIER_COMBO command missing parameters"]
        
        lines = []
        lines.append("  // Teensy 4.0 high-performance modifier combo")
        
        # Press all keys in the combo
        for param in command.parameters:
            if param.upper() in ['MOD', 'CTRL', 'SHIFT', 'ALT']:
                key_code = self._get_teensy_keycode(param.upper())
                lines.append(f"  Keyboard.press({key_code});  // Press {param}")
            else:
                key_code = self._get_teensy_keycode(param)
                lines.append(f"  Keyboard.press({key_code});  // Press {param}")
        
        # Release all keys in reverse order
        for param in reversed(command.parameters):
            if param.upper() in ['MOD', 'CTRL', 'SHIFT', 'ALT']:
                key_code = self._get_teensy_keycode(param.upper())
                lines.append(f"  Keyboard.release({key_code});  // Release {param}")
            else:
                key_code = self._get_teensy_keycode(param)
                lines.append(f"  Keyboard.release({key_code});  // Release {param}")
        
        return lines
    
    def _encode_random_delay_teensy(self, command: HappyFrogCommand) -> List[str]:
        """Encode random delay with Teensy 4.0-specific optimizations."""
        if len(command.parameters) < 2:
            return ["  // ERROR: RANDOM_DELAY command missing min/max values"]
        
        try:
            min_delay = int(command.parameters[0])
            max_delay = int(command.parameters[1])
            
            return [
                f"  // Teensy 4.0 high-precision random delay: {min_delay}ms to {max_delay}ms",
                "  int random_delay = random(min_delay, max_delay);",
                "  delay(random_delay);"
            ]
            
        except ValueError:
            return ["  // ERROR: Invalid random delay values"]
    
    def _encode_standard_command_teensy(self, command: HappyFrogCommand) -> List[str]:
        """Encode standard commands for Teensy 4.0."""
        key_code = self._get_teensy_keycode(command.command_type.value)
        return [
            f"  Keyboard.press({key_code});  // Teensy 4.0 key press: {command.command_type.value}",
            f"  Keyboard.release({key_code});  // Teensy 4.0 key release: {command.command_type.value}"
        ]
    
    def _get_teensy_keycode(self, key: str) -> str:
        """Get Teensy keycode for a key."""
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
        """Get device information for the Teensy 4.0."""
        return {
            'name': self.device_name,
            'processor': self.processor,
            'framework': self.framework,
            'price_range': '$25-35',
            'difficulty': 'Advanced',
            'features': [
                'ARM Cortex-M7 processor (600MHz)',
                '1MB SRAM, 2MB Flash',
                'Extended USB HID support',
                'Hardware crypto acceleration',
                'High-performance capabilities',
                'Advanced security research tool',
                'Teensyduino framework'
            ],
            'setup_notes': [
                'Install Arduino IDE with Teensyduino',
                'Select Teensy 4.0 board',
                'Install required libraries',
                'Upload code to device',
                'Test in controlled environment'
            ]
        } 