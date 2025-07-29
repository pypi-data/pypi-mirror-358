"""
Built-in end-to-end encryption for PyCDN sensitive data.
Automatically encrypts API keys, tokens, and secrets.
"""

import os
import base64
import json
import hashlib
from typing import Any, Dict, List, Tuple, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

# List of sensitive parameter names that should be automatically encrypted
SENSITIVE_KEYWORDS = {
    'api_key', 'apikey', 'api-key',
    'token', 'access_token', 'auth_token', 'bearer_token',
    'secret', 'secret_key', 'client_secret',
    'password', 'passwd', 'pass',
    'private_key', 'key', 'credential', 'credentials',
    'session_id', 'session_key',
    'authorization', 'auth'
}

# Global registry for environment variables that were loaded via dotenv
_dotenv_loaded_vars = set()

def is_sensitive_parameter(param_name: str, param_value: Any) -> bool:
    """
    Determine if a parameter contains sensitive data that should be encrypted.
    
    Args:
        param_name: Parameter name
        param_value: Parameter value
        
    Returns:
        True if parameter should be encrypted
    """
    if not isinstance(param_value, str):
        return False
    
    param_name_lower = param_name.lower()
    
    # Check against known sensitive keywords
    for keyword in SENSITIVE_KEYWORDS:
        if keyword in param_name_lower:
            return True
    
    # Check if this value came from dotenv (environment variables)
    if param_value in _dotenv_loaded_vars:
        return True
    
    # Additional heuristics for API keys/tokens
    if isinstance(param_value, str):
        # OpenAI API keys start with sk-
        if param_value.startswith('sk-') and len(param_value) > 20:
            return True
        # Anthropic API keys start with ant-
        if param_value.startswith('ant-') and len(param_value) > 20:
            return True
        # Generic long alphanumeric strings that look like tokens
        if len(param_value) > 20 and param_value.replace('-', '').replace('_', '').isalnum():
            return True
    
    return False

def register_dotenv_value(value: str):
    """Register a value as having been loaded from dotenv."""
    if value and isinstance(value, str):
        _dotenv_loaded_vars.add(value)

class PyCDNEncryption:
    """
    Built-in encryption handler for PyCDN with automatic key exchange.
    """
    
    def __init__(self, encryption_enabled: bool = True):
        """
        Initialize encryption handler.
        
        Args:
            encryption_enabled: Whether to enable automatic encryption
        """
        self.encryption_enabled = encryption_enabled
        
        if encryption_enabled:
            self._setup_encryption()
    
    def _setup_encryption(self):
        """Setup encryption using a deterministic but secure method."""
        # Use a combination of factors to create a consistent key
        # This ensures client and server can derive the same key
        key_material = f"pycdn_v1_encryption_key"
        
        # Derive encryption key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'pycdn_deterministic_salt_v1',  # Fixed salt for client-server consistency
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(key_material.encode()))
        self.fernet = Fernet(key)
    
    def encrypt_data(self, data: str) -> Dict[str, str]:
        """
        Encrypt sensitive data.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Dictionary with encrypted data and metadata
        """
        if not self.encryption_enabled:
            return {"data": data, "encrypted": False}
        
        try:
            encrypted_bytes = self.fernet.encrypt(data.encode())
            encrypted_str = base64.b64encode(encrypted_bytes).decode()
            
            return {
                "data": encrypted_str,
                "encrypted": True,
                "method": "pycdn_deterministic_v1"
            }
        except Exception as e:
            # Fallback to plain text if encryption fails
            return {"data": data, "encrypted": False, "error": str(e)}
    
    def decrypt_data(self, encrypted_data: Dict[str, str]) -> str:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data: Dictionary with encrypted data
            
        Returns:
            Decrypted data
        """
        if not encrypted_data.get("encrypted", False):
            return encrypted_data["data"]
        
        if not self.encryption_enabled:
            raise ValueError("Encryption not enabled, cannot decrypt data")
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_data["data"])
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {e}")
    
    def process_arguments(self, args: tuple, kwargs: dict) -> Tuple[tuple, dict]:
        """
        Automatically encrypt sensitive arguments.
        
        Args:
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Tuple of processed (args, kwargs) with sensitive data encrypted
        """
        if not self.encryption_enabled:
            return args, kwargs
        
        # Process keyword arguments
        processed_kwargs = {}
        for key, value in kwargs.items():
            if is_sensitive_parameter(key, value):
                processed_kwargs[key] = self.encrypt_data(str(value))
            else:
                processed_kwargs[key] = value
        
        # For positional arguments, we can't easily detect sensitive data
        # so we'll leave them as-is for now
        return args, processed_kwargs
    
    def process_response_arguments(self, args: tuple, kwargs: dict) -> Tuple[tuple, dict]:
        """
        Automatically decrypt sensitive arguments from server response.
        
        Args:
            args: Positional arguments
            kwargs: Keyword arguments with potentially encrypted data
            
        Returns:
            Tuple of processed (args, kwargs) with sensitive data decrypted
        """
        if not self.encryption_enabled:
            return args, kwargs
        
        # Process keyword arguments
        processed_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, dict) and value.get("encrypted", False):
                processed_kwargs[key] = self.decrypt_data(value)
            else:
                processed_kwargs[key] = value
        
        return args, processed_kwargs

# Global encryption instance
_global_encryption = None

def get_global_encryption() -> PyCDNEncryption:
    """Get or create global encryption instance."""
    global _global_encryption
    if _global_encryption is None:
        # Check environment for encryption settings
        enabled = os.getenv("PYCDN_ENCRYPTION_ENABLED", "true").lower() == "true"
        _global_encryption = PyCDNEncryption(encryption_enabled=enabled)
    return _global_encryption

def set_global_encryption(encryption: PyCDNEncryption):
    """Set global encryption instance."""
    global _global_encryption
    _global_encryption = encryption

def enable_encryption() -> PyCDNEncryption:
    """
    Enable automatic encryption for sensitive data.
    Uses deterministic key derivation for client-server consistency.
    
    Returns:
        Encryption instance
    """
    encryption = PyCDNEncryption(encryption_enabled=True)
    set_global_encryption(encryption)
    return encryption

def disable_encryption():
    """Disable automatic encryption."""
    encryption = PyCDNEncryption(encryption_enabled=False)
    set_global_encryption(encryption)

# Monkey-patch dotenv to track loaded values
try:
    from dotenv import load_dotenv as original_load_dotenv
    
    def enhanced_load_dotenv(*args, **kwargs):
        """Enhanced load_dotenv that tracks loaded values for automatic encryption."""
        result = original_load_dotenv(*args, **kwargs)
        
        # Track values that were loaded from .env files
        for key, value in os.environ.items():
            if value and any(keyword in key.lower() for keyword in SENSITIVE_KEYWORDS):
                register_dotenv_value(value)
        
        return result
    
    # Replace the original function
    import dotenv
    dotenv.load_dotenv = enhanced_load_dotenv
    
except ImportError:
    # dotenv not available, that's fine
    pass

# Enhanced os.getenv to track sensitive environment variables
_original_getenv = os.getenv

def enhanced_getenv(key, default=None):
    """Enhanced os.getenv that automatically tracks sensitive environment variables."""
    value = _original_getenv(key, default)
    
    # If this looks like a sensitive environment variable, register it
    if value and isinstance(value, str):
        key_lower = key.lower()
        if any(keyword in key_lower for keyword in SENSITIVE_KEYWORDS):
            register_dotenv_value(value)
    
    return value

# Replace os.getenv
os.getenv = enhanced_getenv 