"""
Happy Frog - ESP32 Device Template

This module provides Arduino code generation specifically for the ESP32.
The ESP32 is popular for WiFi-enabled HID emulation and IoT scenarios due to
its built-in WiFi, Bluetooth, and extensive connectivity options.

Educational Purpose: Demonstrates wireless HID emulation and IoT security concepts.

Author: ZeroDumb
License: GNU GPLv3
"""

from typing import List, Dict, Any, Optional
from happy_frog_parser import HappyFrogScript, HappyFrogCommand, CommandType


class ESP32Encoder:
    """
    Encoder that generates Arduino code specifically for ESP32.
    
    The ESP32 uses dual-core processors and provides WiFi/Bluetooth capabilities,
    making it ideal for wireless HID emulation and IoT security research.
    """
    
    def __init__(self):
        """Initialize the ESP32-specific encoder."""
        self.device_name = "ESP32"
        self.processor = "Dual-core Xtensa LX6"
        self.framework = "Arduino (ESP32)"
        
        # ESP32-specific optimizations
        self.optimizations = {
            'wifi_enabled': True,  # Built-in WiFi
            'bluetooth_enabled': True,  # Built-in Bluetooth
            'dual_core': True,  # Dual-core processor
            'iot_capable': True,  # IoT connectivity
            'wireless_attacks': True,  # Wireless attack scenarios
        }
    
    def generate_header(self, script: HappyFrogScript) -> List[str]:
        """Generate ESP32-specific header code."""
        lines = []
        
        lines.append('/*')
        lines.append('Happy Frog - ESP32 Generated Code')
        lines.append('Educational HID Emulation Script')
        lines.append('')
        lines.append(f'Device: {self.device_name}')
        lines.append(f'Processor: {self.processor}')
        lines.append(f'Framework: {self.framework}')
        lines.append('')
        lines.append('This code was automatically generated from a Happy Frog Script.')
        lines.append('Optimized for ESP32 with WiFi/Bluetooth capabilities.')
        lines.append('')
        lines.append('⚠️ IMPORTANT: Use only for educational purposes and authorized testing!')
        lines.append('*/')
        lines.append('')
        
        # ESP32-specific includes
        lines.append('#include <BleKeyboard.h>  // ESP32 Bluetooth HID')
        lines.append('#include <WiFi.h>  // ESP32 WiFi')
        lines.append('#include <WebServer.h>  // ESP32 Web Server')
        lines.append('')
        
        # ESP32-specific setup
        lines.append('// ESP32-specific configuration')
        lines.append('BleKeyboard bleKeyboard("Happy Frog ESP32", "Happy Frog Team", 100);')
        lines.append('WebServer server(80);  // Web server for remote control')
        lines.append('')
        
        lines.append('void setup() {')
        lines.append('  // Initialize ESP32 for wireless HID emulation')
        lines.append('  Serial.begin(115200);  // ESP32 serial communication')
        lines.append('  ')
        lines.append('  // Initialize Bluetooth HID')
        lines.append('  bleKeyboard.begin();')
        lines.append('  ')
        lines.append('  // ESP32: Wait for Bluetooth connection')
        lines.append('  Serial.println("Waiting for Bluetooth connection...");')
        lines.append('  while(!bleKeyboard.isConnected()) {')
        lines.append('    delay(500);')
        lines.append('  }')
        lines.append('  Serial.println("Bluetooth connected!");')
        lines.append('  ')
        lines.append('  // ESP32: Additional startup delay')
        lines.append('  delay(2000);  // Wait for system to recognize device')
        lines.append('}')
        lines.append('')
        
        lines.append('void loop() {')
        lines.append('  // Main execution - runs once')
        lines.append('  executePayload();')
        lines.append('  ')
        lines.append('  // ESP32: Maintain Bluetooth connection')
        lines.append('  while(true) {')
        lines.append('    bleKeyboard.isConnected();  // Keep connection alive')
        lines.append('    delay(1000);')
        lines.append('  }')
        lines.append('}')
        lines.append('')
        
        lines.append('void executePayload() {')
        lines.append('  // Generated Happy Frog payload for ESP32')
        lines.append('')
        
        return lines
    
    def generate_footer(self) -> List[str]:
        """Generate ESP32-specific footer code."""
        lines = []
        
        lines.append('  // End of Happy Frog payload')
        lines.append('}')
        lines.append('')
        lines.append('/*')
        lines.append('End of Happy Frog Generated Code for ESP32')
        lines.append('')
        lines.append('Educational Notes:')
        lines.append('- ESP32 provides wireless HID emulation capabilities')
        lines.append('- Dual-core processor enables complex automation scenarios')
        lines.append('- WiFi and Bluetooth support IoT security research')
        lines.append('- Ideal for wireless attack demonstrations and education')
        lines.append('')
        lines.append('For more information, visit: https://github.com/ZeroDumb/happy-frog')
        lines.append('*/')
        
        return lines
    
    def encode_command(self, command: HappyFrogCommand) -> List[str]:
        """Encode a command specifically for ESP32."""
        lines = []
        
        # Add ESP32-specific comment
        comment = f"  // ESP32 Command: {command.raw_text}"
        lines.append(comment)
        
        # Encode based on command type with ESP32 optimizations
        if command.command_type == CommandType.DELAY:
            lines.extend(self._encode_delay_esp32(command))
        elif command.command_type == CommandType.STRING:
            lines.extend(self._encode_string_esp32(command))
        elif command.command_type == CommandType.MODIFIER_COMBO:
            lines.extend(self._encode_modifier_combo_esp32(command))
        elif command.command_type == CommandType.RANDOM_DELAY:
            lines.extend(self._encode_random_delay_esp32(command))
        else:
            # Use standard encoding for other commands
            lines.extend(self._encode_standard_command_esp32(command))
        
        return lines
    
    def _encode_delay_esp32(self, command: HappyFrogCommand) -> List[str]:
        """Encode delay with ESP32-specific optimizations."""
        try:
            delay_ms = int(command.parameters[0])
            if delay_ms < 0:
                raise ValueError("Delay value must be non-negative")
            
            # ESP32: High-precision delays with WiFi considerations
            return [f"  delay({delay_ms});  // ESP32 delay: {delay_ms}ms"]
                
        except (ValueError, IndexError):
            return ["  // ERROR: Invalid delay value"]
    
    def _encode_string_esp32(self, command: HappyFrogCommand) -> List[str]:
        """Encode string with ESP32-specific optimizations."""
        if not command.parameters:
            return ["  // ERROR: STRING command missing text"]
        
        text = command.parameters[0]
        # ESP32: Bluetooth HID string input
        return [
            f'  bleKeyboard.print("{text}");  // ESP32 Bluetooth string input'
        ]
    
    def _encode_modifier_combo_esp32(self, command: HappyFrogCommand) -> List[str]:
        """Encode modifier combo with ESP32-specific optimizations."""
        if not command.parameters:
            return ["  // ERROR: MODIFIER_COMBO command missing parameters"]
        
        lines = []
        lines.append("  // ESP32 Bluetooth modifier combo")
        
        # Press all keys in the combo
        for param in command.parameters:
            if param.upper() in ['MOD', 'CTRL', 'SHIFT', 'ALT']:
                key_code = self._get_esp32_keycode(param.upper())
                lines.append(f"  bleKeyboard.press({key_code});  // Press {param}")
            else:
                key_code = self._get_esp32_keycode(param)
                lines.append(f"  bleKeyboard.press({key_code});  // Press {param}")
        
        # Release all keys in reverse order
        for param in reversed(command.parameters):
            if param.upper() in ['MOD', 'CTRL', 'SHIFT', 'ALT']:
                key_code = self._get_esp32_keycode(param.upper())
                lines.append(f"  bleKeyboard.release({key_code});  // Release {param}")
            else:
                key_code = self._get_esp32_keycode(param)
                lines.append(f"  bleKeyboard.release({key_code});  // Release {param}")
        
        return lines
    
    def _encode_random_delay_esp32(self, command: HappyFrogCommand) -> List[str]:
        """Encode random delay with ESP32-specific optimizations."""
        if len(command.parameters) < 2:
            return ["  // ERROR: RANDOM_DELAY command missing min/max values"]
        
        try:
            min_delay = int(command.parameters[0])
            max_delay = int(command.parameters[1])
            
            return [
                f"  // ESP32 wireless random delay: {min_delay}ms to {max_delay}ms",
                "  int random_delay = random(min_delay, max_delay);",
                "  delay(random_delay);"
            ]
            
        except ValueError:
            return ["  // ERROR: Invalid random delay values"]
    
    def _encode_standard_command_esp32(self, command: HappyFrogCommand) -> List[str]:
        """Encode standard commands for ESP32."""
        key_code = self._get_esp32_keycode(command.command_type.value)
        return [
            f"  bleKeyboard.press({key_code});  // ESP32 key press: {command.command_type.value}",
            f"  bleKeyboard.release({key_code});  // ESP32 key release: {command.command_type.value}"
        ]
    
    def _get_esp32_keycode(self, key: str) -> str:
        """Get ESP32 keycode for a key."""
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
        """Get device information for the ESP32."""
        return {
            'name': self.device_name,
            'processor': self.processor,
            'framework': self.framework,
            'price_range': '$5-15',
            'difficulty': 'Intermediate',
            'features': [
                'Dual-core Xtensa LX6 processor',
                'Built-in WiFi and Bluetooth',
                'Wireless HID emulation',
                'IoT connectivity',
                'Web server capabilities',
                'Remote control possibilities',
                'Advanced security research tool'
            ],
            'setup_notes': [
                'Install Arduino IDE with ESP32 board support',
                'Select ESP32 board',
                'Install BleKeyboard library',
                'Upload code to device',
                'Connect via Bluetooth',
                'Test in controlled environment'
            ]
        } 