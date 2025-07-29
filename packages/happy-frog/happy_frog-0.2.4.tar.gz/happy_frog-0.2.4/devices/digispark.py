"""
Happy Frog - DigiSpark Device Template

This module provides Arduino code generation specifically for the DigiSpark.
The DigiSpark is an ultra-compact device popular for portable payloads due to
its small size and built-in USB HID capabilities.

Educational Purpose: Demonstrates ultra-compact device optimization and portable applications.

Author: ZeroDumb
License: GNU GPLv3
"""

from typing import List, Dict, Any, Optional
from happy_frog_parser import HappyFrogScript, HappyFrogCommand, CommandType


class DigiSparkEncoder:
    """
    Encoder that generates Arduino code specifically for DigiSpark.
    
    The DigiSpark uses the ATtiny85 processor and provides ultra-compact
    HID emulation capabilities in a tiny form factor.
    """
    
    def __init__(self):
        """Initialize the DigiSpark-specific encoder."""
        self.device_name = "DigiSpark"
        self.processor = "ATtiny85"
        self.framework = "Arduino (DigiSpark)"
        
        # DigiSpark-specific optimizations
        self.optimizations = {
            'ultra_compact': True,  # Tiny form factor
            'built_in_usb': True,  # Built-in USB HID
            'low_power': True,  # Low power consumption
            'portable': True,  # Highly portable
            'limited_memory': True,  # 8KB flash, 512B RAM
        }
    
    def generate_header(self, script: HappyFrogScript) -> List[str]:
        """Generate DigiSpark-specific header code."""
        lines = []
        
        lines.append('/*')
        lines.append('Happy Frog - DigiSpark Generated Code')
        lines.append('Educational HID Emulation Script')
        lines.append('')
        lines.append(f'Device: {self.device_name}')
        lines.append(f'Processor: {self.processor}')
        lines.append(f'Framework: {self.framework}')
        lines.append('')
        lines.append('This code was automatically generated from a Happy Frog Script.')
        lines.append('Optimized for DigiSpark with ATtiny85 processor.')
        lines.append('')
        lines.append('⚠️ IMPORTANT: Use only for educational purposes and authorized testing!')
        lines.append('*/')
        lines.append('')
        
        # DigiSpark-specific includes
        lines.append('#include "DigiKeyboard.h"  // DigiSpark keyboard library')
        lines.append('')
        
        # DigiSpark-specific setup
        lines.append('void setup() {')
        lines.append('  // Initialize DigiSpark for ultra-compact HID emulation')
        lines.append('  // DigiSpark: No explicit initialization needed')
        lines.append('  ')
        lines.append('  // DigiSpark: Minimal startup delay for stealth')
        lines.append('  delay(1000);  // Compact startup delay')
        lines.append('}')
        lines.append('')
        
        lines.append('void loop() {')
        lines.append('  // Main execution - runs once')
        lines.append('  executePayload();')
        lines.append('  ')
        lines.append('  // DigiSpark: Minimal infinite loop')
        lines.append('  while(true) {')
        lines.append('    ;  // Empty loop to prevent re-execution')
        lines.append('  }')
        lines.append('}')
        lines.append('')
        
        lines.append('void executePayload() {')
        lines.append('  // Generated Happy Frog payload for DigiSpark')
        lines.append('')
        
        return lines
    
    def generate_footer(self) -> List[str]:
        """Generate DigiSpark-specific footer code."""
        lines = []
        
        lines.append('  // End of Happy Frog payload')
        lines.append('}')
        lines.append('')
        lines.append('/*')
        lines.append('End of Happy Frog Generated Code for DigiSpark')
        lines.append('')
        lines.append('Educational Notes:')
        lines.append('- DigiSpark provides ultra-compact HID emulation')
        lines.append('- ATtiny85 processor enables portable applications')
        lines.append('- Built-in USB HID support in tiny form factor')
        lines.append('- Ideal for educational portable payload demonstrations')
        lines.append('')
        lines.append('For more information, visit: https://github.com/ZeroDumb/happy-frog')
        lines.append('*/')
        
        return lines
    
    def encode_command(self, command: HappyFrogCommand) -> List[str]:
        """Encode a command specifically for DigiSpark."""
        lines = []
        
        # Add DigiSpark-specific comment
        comment = f"  // DigiSpark Command: {command.raw_text}"
        lines.append(comment)
        
        # Encode based on command type with DigiSpark optimizations
        if command.command_type == CommandType.DELAY:
            lines.extend(self._encode_delay_digispark(command))
        elif command.command_type == CommandType.STRING:
            lines.extend(self._encode_string_digispark(command))
        elif command.command_type == CommandType.MODIFIER_COMBO:
            lines.extend(self._encode_modifier_combo_digispark(command))
        elif command.command_type == CommandType.RANDOM_DELAY:
            lines.extend(self._encode_random_delay_digispark(command))
        else:
            # Use standard encoding for other commands
            lines.extend(self._encode_standard_command_digispark(command))
        
        return lines
    
    def _encode_delay_digispark(self, command: HappyFrogCommand) -> List[str]:
        """Encode delay with DigiSpark-specific optimizations."""
        try:
            delay_ms = int(command.parameters[0])
            if delay_ms < 0:
                raise ValueError("Delay value must be non-negative")
            
            # DigiSpark: Compact delay implementation
            return [f"  DigiKeyboard.delay({delay_ms});  // DigiSpark delay: {delay_ms}ms"]
                
        except (ValueError, IndexError):
            return ["  // ERROR: Invalid delay value"]
    
    def _encode_string_digispark(self, command: HappyFrogCommand) -> List[str]:
        """Encode string with DigiSpark-specific optimizations."""
        if not command.parameters:
            return ["  // ERROR: STRING command missing text"]
        
        text = command.parameters[0]
        # DigiSpark: Compact string input
        return [
            f'  DigiKeyboard.print("{text}");  // DigiSpark string input'
        ]
    
    def _encode_modifier_combo_digispark(self, command: HappyFrogCommand) -> List[str]:
        """Encode modifier combo with DigiSpark-specific optimizations."""
        if not command.parameters:
            return ["  // ERROR: MODIFIER_COMBO command missing parameters"]
        
        lines = []
        lines.append("  // DigiSpark compact modifier combo")
        
        # Press all keys in the combo
        for param in command.parameters:
            if param.upper() in ['MOD', 'CTRL', 'SHIFT', 'ALT']:
                key_code = self._get_digispark_keycode(param.upper())
                lines.append(f"  DigiKeyboard.sendKeyPress({key_code});  // Press {param}")
            else:
                key_code = self._get_digispark_keycode(param)
                lines.append(f"  DigiKeyboard.sendKeyPress({key_code});  // Press {param}")
        
        return lines
    
    def _encode_random_delay_digispark(self, command: HappyFrogCommand) -> List[str]:
        """Encode random delay with DigiSpark-specific optimizations."""
        if len(command.parameters) < 2:
            return ["  // ERROR: RANDOM_DELAY command missing min/max values"]
        
        try:
            min_delay = int(command.parameters[0])
            max_delay = int(command.parameters[1])
            
            return [
                f"  // DigiSpark compact random delay: {min_delay}ms to {max_delay}ms",
                "  int random_delay = random(min_delay, max_delay);",
                "  DigiKeyboard.delay(random_delay);"
            ]
            
        except ValueError:
            return ["  // ERROR: Invalid random delay values"]
    
    def _encode_standard_command_digispark(self, command: HappyFrogCommand) -> List[str]:
        """Encode standard commands for DigiSpark."""
        key_code = self._get_digispark_keycode(command.command_type.value)
        return [
            f"  DigiKeyboard.sendKeyPress({key_code});  // DigiSpark key press: {command.command_type.value}"
        ]
    
    def _get_digispark_keycode(self, key: str) -> str:
        """Get DigiSpark keycode for a key."""
        key = key.upper()
        
        # Modifier keys
        if key == 'MOD':
            return "KEY_GUI"
        elif key == 'CTRL':
            return "KEY_CTRL"
        elif key == 'SHIFT':
            return "KEY_SHIFT"
        elif key == 'ALT':
            return "KEY_ALT"
        
        # Single letter keys
        if len(key) == 1 and key.isalpha():
            return f"KEY_{key}"
        
        # Number keys
        if key.isdigit():
            return f"KEY_{key}"
        
        # Special mappings
        key_mappings = {
            'ENTER': 'KEY_ENTER',
            'SPACE': 'KEY_SPACE',
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
        
        return key_mappings.get(key, f"KEY_{key}")
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get device information for the DigiSpark."""
        return {
            'name': self.device_name,
            'processor': self.processor,
            'framework': self.framework,
            'price_range': '$2-5',
            'difficulty': 'Beginner',
            'features': [
                'ATtiny85 processor',
                'Ultra-compact form factor',
                'Built-in USB HID support',
                'Low power consumption',
                'Highly portable',
                'Very low cost',
                'Perfect for educational demonstrations'
            ],
            'setup_notes': [
                'Install Arduino IDE with DigiSpark board support',
                'Select DigiSpark board',
                'Install DigiKeyboard library',
                'Upload code to device',
                'Test in controlled environment'
            ]
        } 