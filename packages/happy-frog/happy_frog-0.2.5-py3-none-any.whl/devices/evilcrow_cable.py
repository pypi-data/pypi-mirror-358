from typing import List, Dict, Any
from happy_frog_parser import HappyFrogScript, HappyFrogCommand, CommandType

class EvilCrowCableEncoder:
    """
    Encoder that generates Arduino code specifically for EvilCrow-Cable.
    
    The EvilCrow-Cable uses ATtiny85 microcontrollers with specialized
    hardware for BadUSB attacks, including built-in USB-C connectors.
    """
    
    def __init__(self):
        """Initialize the EvilCrow-Cable-specific encoder."""
        self.device_name = "EvilCrow-Cable"
        self.processor = "ATtiny85"
        self.framework = "Arduino (EvilCrow-Cable)"
        
        # EvilCrow-Cable-specific optimizations
        self.optimizations = {
            'built_in_usb_c': True,  # Built-in USB-C connectors
            'stealth_design': True,  # Designed for stealth operations
            'badusb_optimized': True,  # Optimized for BadUSB attacks
            'compact_form': True,  # Ultra-compact form factor
            'limited_memory': True,  # 8KB flash, 512B RAM
            'specialized_hardware': True,  # Custom hardware design
        }
    
    def generate_header(self, script: HappyFrogScript) -> List[str]:
        """Generate EvilCrow-Cable-specific header code."""
        lines = []
        
        lines.append('/*')
        lines.append('Happy Frog - EvilCrow-Cable Generated Code')
        lines.append('Educational HID Emulation Script')
        lines.append('')
        lines.append(f'Device: {self.device_name}')
        lines.append(f'Processor: {self.processor}')
        lines.append(f'Framework: {self.framework}')
        lines.append('')
        lines.append('This code was automatically generated from a Happy Frog Script.')
        lines.append('Optimized for EvilCrow-Cable with ATtiny85 processor.')
        lines.append('')
        lines.append('⚠️ IMPORTANT: Use only for educational purposes and authorized testing!')
        lines.append('⚠️ This device is designed for cybersecurity education and research.')
        lines.append('*/')
        lines.append('')
        
        # EvilCrow-Cable-specific includes
        lines.append('#include "DigiKeyboard.h"  // EvilCrow-Cable keyboard library')
        lines.append('')
        
        # EvilCrow-Cable-specific setup
        lines.append('void setup() {')
        lines.append('  // Initialize EvilCrow-Cable for stealth HID emulation')
        lines.append('  // EvilCrow-Cable: No explicit initialization needed')
        lines.append('  ')
        lines.append('  // EvilCrow-Cable: Minimal startup delay for maximum stealth')
        lines.append('  DigiKeyboard.delay(1000);  // Stealth startup delay')
        lines.append('}')
        lines.append('')
        
        lines.append('void loop() {')
        lines.append('  // Main execution - runs once')
        lines.append('  executePayload();')
        lines.append('  ')
        lines.append('  // EvilCrow-Cable: Stealth infinite loop')
        lines.append('  while(true) {')
        lines.append('    ;  // Empty loop to prevent re-execution')
        lines.append('  }')
        lines.append('}')
        lines.append('')
        
        lines.append('void executePayload() {')
        lines.append('  // Generated Happy Frog payload for EvilCrow-Cable')
        lines.append('')
        
        return lines
    
    def generate_footer(self) -> List[str]:
        """Generate EvilCrow-Cable-specific footer code."""
        lines = []
        
        lines.append('  // End of Happy Frog payload')
        lines.append('}')
        lines.append('')
        lines.append('/*')
        lines.append('End of Happy Frog Generated Code for EvilCrow-Cable')
        lines.append('')
        lines.append('Educational Notes:')
        lines.append('- EvilCrow-Cable provides ultra-stealth HID emulation')
        lines.append('- ATtiny85 processor enables portable attack scenarios')
        lines.append('- Built-in USB-C connectors for maximum compatibility')
        lines.append('- Designed for cybersecurity education and research')
        lines.append('- Use responsibly and ethically!')
        lines.append('')
        lines.append('For more information, visit: https://github.com/ZeroDumb/happy-frog')
        lines.append('*/')
        
        return lines
    
    def encode_command(self, command: HappyFrogCommand) -> List[str]:
        """Encode a command specifically for EvilCrow-Cable."""
        lines = []
        
        # Add EvilCrow-Cable-specific comment
        comment = f"  // EvilCrow-Cable Command: {command.raw_text}"
        lines.append(comment)
        
        # Encode based on command type with EvilCrow-Cable optimizations
        if command.command_type == CommandType.DELAY:
            lines.extend(self._encode_delay_evilcrow(command))
        elif command.command_type == CommandType.STRING:
            lines.extend(self._encode_string_evilcrow(command))
        elif command.command_type == CommandType.MODIFIER_COMBO:
            lines.extend(self._encode_modifier_combo_evilcrow(command))
        elif command.command_type == CommandType.RANDOM_DELAY:
            lines.extend(self._encode_random_delay_evilcrow(command))
        else:
            # Use standard encoding for other commands
            lines.extend(self._encode_standard_command_evilcrow(command))
        
        return lines
    
    def _encode_delay_evilcrow(self, command: HappyFrogCommand) -> List[str]:
        """Encode delay with EvilCrow-Cable-specific optimizations."""
        try:
            delay_ms = int(command.parameters[0])
            if delay_ms < 0:
                raise ValueError("Delay value must be non-negative")
            
            # EvilCrow-Cable: Stealth delay implementation
            return [f"  DigiKeyboard.delay({delay_ms});  // EvilCrow-Cable delay: {delay_ms}ms"]
                
        except (ValueError, IndexError):
            return ["  // ERROR: Invalid delay value"]
    
    def _encode_string_evilcrow(self, command: HappyFrogCommand) -> List[str]:
        """Encode string with EvilCrow-Cable-specific optimizations."""
        if not command.parameters:
            return ["  // ERROR: STRING command missing text"]
        
        text = command.parameters[0]
        # EvilCrow-Cable: Stealth string input
        return [
            f'  DigiKeyboard.print("{text}");  // EvilCrow-Cable string input'
        ]
    
    def _encode_modifier_combo_evilcrow(self, command: HappyFrogCommand) -> List[str]:
        """Encode modifier combo with EvilCrow-Cable-specific optimizations."""
        if not command.parameters:
            return ["  // ERROR: MODIFIER_COMBO command missing parameters"]
        
        lines = []
        lines.append("  // EvilCrow-Cable stealth modifier combo")
        
        # Press all keys in the combo
        for param in command.parameters:
            if param.upper() in ['MOD', 'CTRL', 'SHIFT', 'ALT']:
                key_code = self._get_evilcrow_keycode(param.upper())
                lines.append(f"  DigiKeyboard.sendKeyPress({key_code});  // Press {param}")
            else:
                key_code = self._get_evilcrow_keycode(param)
                lines.append(f"  DigiKeyboard.sendKeyPress({key_code});  // Press {param}")
        
        return lines
    
    def _encode_random_delay_evilcrow(self, command: HappyFrogCommand) -> List[str]:
        """Encode random delay with EvilCrow-Cable-specific optimizations."""
        if len(command.parameters) < 2:
            return ["  // ERROR: RANDOM_DELAY command missing min/max values"]
        
        try:
            min_delay = int(command.parameters[0])
            max_delay = int(command.parameters[1])
            
            return [
                f"  // EvilCrow-Cable stealth random delay: {min_delay}ms to {max_delay}ms",
                "  int random_delay = random(min_delay, max_delay);",
                "  DigiKeyboard.delay(random_delay);"
            ]
            
        except ValueError:
            return ["  // ERROR: Invalid random delay values"]
    
    def _encode_standard_command_evilcrow(self, command: HappyFrogCommand) -> List[str]:
        """Encode standard commands for EvilCrow-Cable."""
        key_code = self._get_evilcrow_keycode(command.command_type.value)
        return [
            f"  DigiKeyboard.sendKeyPress({key_code});  // EvilCrow-Cable key press: {command.command_type.value}"
        ]
    
    def _get_evilcrow_keycode(self, key: str) -> str:
        """Get EvilCrow-Cable keycode for a key."""
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
        
        # Special keys
        elif key == 'ENTER':
            return "KEY_ENTER"
        elif key == 'TAB':
            return "KEY_TAB"
        elif key == 'ESC':
            return "KEY_ESC"
        elif key == 'ESCAPE':
            return "KEY_ESC"
        elif key == 'SPACE':
            return "KEY_SPACE"
        elif key == 'DELETE':
            return "KEY_DELETE"
        elif key == 'BACKSPACE':
            return "KEY_BACKSPACE"
        
        # Arrow keys
        elif key == 'UP':
            return "KEY_UP_ARROW"
        elif key == 'DOWN':
            return "KEY_DOWN_ARROW"
        elif key == 'LEFT':
            return "KEY_LEFT_ARROW"
        elif key == 'RIGHT':
            return "KEY_RIGHT_ARROW"
        
        # Function keys
        elif key in ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']:
            return f"KEY_{key}"
        
        # Navigation keys
        elif key == 'HOME':
            return "KEY_HOME"
        elif key == 'END':
            return "KEY_END"
        elif key == 'PAGE_UP':
            return "KEY_PAGE_UP"
        elif key == 'PAGE_DOWN':
            return "KEY_PAGE_DOWN"
        elif key == 'INSERT':
            return "KEY_INSERT"
        
        # Single character keys
        elif len(key) == 1:
            if key.isalpha():
                return f"KEY_{key}"
            elif key.isdigit():
                return f"KEY_{key}"
            else:
                # Handle special characters
                special_chars = {
                    '!': 'KEY_1', '@': 'KEY_2', '#': 'KEY_3', '$': 'KEY_4',
                    '%': 'KEY_5', '^': 'KEY_6', '&': 'KEY_7', '*': 'KEY_8',
                    '(': 'KEY_9', ')': 'KEY_0', '-': 'KEY_MINUS', '=': 'KEY_EQUAL',
                    '[': 'KEY_LEFT_BRACE', ']': 'KEY_RIGHT_BRACE',
                    '\\': 'KEY_BACKSLASH', ';': 'KEY_SEMICOLON',
                    "'": 'KEY_QUOTE', ',': 'KEY_COMMA', '.': 'KEY_PERIOD',
                    '/': 'KEY_SLASH', '`': 'KEY_TILDE'
                }
                return special_chars.get(key, f"KEY_{key}")
        
        else:
            return f"KEY_{key}"
    
    def get_device_info(self) -> Dict[str, Any]:
        return {
            'device_name': self.device_name,
            'processor': self.processor,
            'framework': self.framework,
            'optimizations': self.optimizations,
            'notes': 'Generates Arduino code for EvilCrow-Cable. Copy output to device as code.ino',
            'warnings': [
                'This device is designed for cybersecurity education and research',
                'Use only for authorized testing and educational purposes',
                'Ensure compliance with local laws and regulations'
            ]
        } 