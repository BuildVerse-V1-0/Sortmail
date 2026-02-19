"""
Data Encryption Utilities
-------------------------
Handles AES-256-GCM encryption for sensitive data at rest (OAuth tokens).
"""

import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class DataEncryption:
    _cipher: AESGCM = None

    @classmethod
    def get_cipher(cls) -> AESGCM:
        """Get or create the AESGCM cipher instance."""
        if cls._cipher is None:
            # key must be 32 bytes (256 bits) URL-safe base64 encoded
            from app.config import settings
            key_b64 = settings.ENCRYPTION_KEY or os.getenv("ENCRYPTION_KEY", "")
            
            if not key_b64:
                # Retrieve from secrets manager or fallback for dev
                if settings.ENVIRONMENT == "production":
                    # In production, we should ideally fail, but for now we warn loudly to avoid boot loops if key is missing
                    print("🚨 CRITICAL WARNING: ENCRYPTION_KEY missing in PRODUCTION. Generating temporary key (DATA LOSS ON RESTART).")
                else:
                    print("⚠️ WARNING: No ENCRYPTION_KEY found (Dev). Generating temporary key.")
                    
                key = AESGCM.generate_key(bit_length=256)
            else:
                try:
                    key = base64.urlsafe_b64decode(key_b64)
                except Exception as e:
                     # Attempt standard b64 decode if urlsafe fails
                    key = base64.b64decode(key_b64)

            cls._cipher = AESGCM(key)
        return cls._cipher

    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        """Encrypt plaintext string using AES-256-GCM."""
        if not plaintext:
            return ""
            
        cipher = cls.get_cipher()
        nonce = os.urandom(12) # GCM standard nonce size
        
        # distinct nonce for each encryption
        ciphertext = cipher.encrypt(nonce, plaintext.encode("utf-8"), None)
        
        # Return nonce + ciphertext encoded in base64
        return base64.urlsafe_b64encode(nonce + ciphertext).decode("utf-8")

    @classmethod
    def decrypt(cls, encrypted_data: str) -> str:
        """Decrypt base64 encoded nonce+ciphertext."""
        if not encrypted_data:
            return ""
            
        cipher = cls.get_cipher()
        
        try:
            data = base64.urlsafe_b64decode(encrypted_data)
            nonce = data[:12]
            ciphertext = data[12:]
            
            plaintext = cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode("utf-8")
        except Exception as e:
            # Log decryption failure
            print(f"Decryption failed: {str(e)}")
            raise ValueError("Invalid encrypted data")

# Helper aliases
encrypt_token = DataEncryption.encrypt
decrypt_token = DataEncryption.decrypt
