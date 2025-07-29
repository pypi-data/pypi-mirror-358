"""
Happy Frog - Payload Examples Package

This package contains educational payload examples for Happy Frog Script.
These are demonstration scripts showing various automation and HID emulation concepts.

Educational Purpose: These demonstrate scripting techniques, automation patterns,
and educational cybersecurity concepts.

Author: ZeroDumb
License: GNU GPLv3
"""

import os
import pkg_resources

def get_payload_path(filename):
    """Get the full path to a payload file in this package."""
    return pkg_resources.resource_filename(__name__, filename)

def list_payloads():
    """List all available payload files."""
    payload_dir = pkg_resources.resource_filename(__name__, "")
    payloads = []
    for file in os.listdir(payload_dir):
        if file.endswith('.txt') and not file.startswith('.'):
            payloads.append(file)
    return sorted(payloads)

def load_payload(filename):
    """Load a payload file and return its contents."""
    try:
        with open(get_payload_path(filename), 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Payload file '{filename}' not found")

__version__ = "1.0.0"
__author__ = "ZeroDumb"
__license__ = "GNU GPLv3"

__all__ = [
    "get_payload_path",
    "list_payloads", 
    "load_payload",
] 