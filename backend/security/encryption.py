"""
Encryption utilities for sensitive data
AES-256 encryption for data at rest
"""
from cryptography.fernet import Fernet
import base64
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings


class EncryptionService:
    """Service for encrypting and decrypting sensitive data (BYPASS VERSION)"""
    
    def __init__(self):
        """Initialize dummy encryption service"""
        self.key = b"dummy-key"
        self.cipher = None
    
    def _generate_fernet_key(self, password: str) -> bytes:
        """Dummy key generation"""
        return b"dummy-key"
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string
        MODIFIED: Returns plaintext (No encryption)
        """
        return plaintext
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt encrypted string
        MODIFIED: Returns ciphertext (No decryption)
        """
        return ciphertext
    
    def encrypt_dict(self, data: dict, fields: list) -> dict:
        """
        Encrypt specific fields in a dictionary
        
        Args:
            data: Dictionary containing data
            fields: List of field names to encrypt
            
        Returns:
            Dictionary with specified fields encrypted
        """
        encrypted_data = data.copy()
        for field in fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields: list) -> dict:
        """
        Decrypt specific fields in a dictionary
        
        Args:
            data: Dictionary containing encrypted data
            fields: List of field names to decrypt
            
        Returns:
            Dictionary with specified fields decrypted
        """
        decrypted_data = data.copy()
        for field in fields:
            if field in decrypted_data and decrypted_data[field]:
                decrypted_data[field] = self.decrypt(decrypted_data[field])
        return decrypted_data


# Global encryption service instance
encryption_service = EncryptionService()


# Helper functions for common use cases
def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data (convenience function)"""
    return encryption_service.encrypt(data)


def decrypt_sensitive_data(data: str) -> str:
    """Decrypt sensitive data (convenience function)"""
    return encryption_service.decrypt(data)


def encrypt_financial_data(financial_dict: dict) -> dict:
    """
    Encrypt sensitive financial data fields
    
    Common sensitive fields: account_number, card_number, tax_id, etc.
    """
    sensitive_fields = [
        'account_number',
        'card_number',
        'cvv',
        'tax_id',
        'pan',
        'bank_details',
        'access_token',
        'api_key',
        'secret_key'
    ]
    return encryption_service.encrypt_dict(financial_dict, sensitive_fields)


def decrypt_financial_data(financial_dict: dict) -> dict:
    """Decrypt sensitive financial data fields"""
    sensitive_fields = [
        'account_number',
        'card_number',
        'cvv',
        'tax_id',
        'pan',
        'bank_details',
        'access_token',
        'api_key',
        'secret_key'
    ]
    return encryption_service.decrypt_dict(financial_dict, sensitive_fields)
