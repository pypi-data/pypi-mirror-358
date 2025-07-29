"""
Happy Frog - Script Parser Package

This package provides parsing and encoding functionality for Happy Frog Script,
an educational scripting language for HID emulation on microcontrollers.

Educational Purpose: This demonstrates language parsing, code generation,
and microcontroller programming concepts.

Author: ZeroDumb
License: GNU GPLv3
"""

from .parser import (
    HappyFrogParser,
    HappyFrogScript,
    HappyFrogCommand,
    CommandType,
    HappyFrogScriptError
)

from .encoder import (
    CircuitPythonEncoder,
    EncoderError
)

try:
    from ._version import __version__, __version_tuple__
except ImportError:
    __version__ = "0.1.0"
    __version_tuple__ = (0, 1, 0)

__author__ = "ZeroDumb"
__license__ = "GNU GPLv3"

__all__ = [
    # Parser classes
    "HappyFrogParser",
    "HappyFrogScript", 
    "HappyFrogCommand",
    "CommandType",
    "HappyFrogScriptError",
    
    # Encoder classes
    "CircuitPythonEncoder",
    "EncoderError",
    
    # Version info
    "__version__",
    "__version_tuple__",
] 