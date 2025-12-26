"""
Vaultwarden API Integration for Vertex Genesis v1.1.1
Enables dynamic credential management and secure storage.
"""

import os
import httpx
import secrets
import string
import logging
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class VaultManager:
    """
    Manages interactions with Vaultwarden for secure credential storage.
    Supports dynamic password generation and 2FA artifact creation.
    """
    
    def __init__(self):
        self.vault_url = os.getenv("VAULTWARDEN_URL", "http://vaultwarden:80")
        self.admin_token = os.getenv("VAULTWARDEN_ADMIN_TOKEN")
        self.client = httpx.AsyncClient(timeout=30.0)
        self.access_token: Optional[str] = None
        
        if not self.admin_token:
            logger.warning("⚠️ VAULTWARDEN_ADMIN_TOKEN not set. Vault features disabled.")
    
    def generate_password(self, length: int = 32, include_symbols: bool = True) -> str:
        """
        Generate a cryptographically secure random password.
        
        Args:
            length: Password length (default 32)
            include_symbols: Include special characters (default True)
        
        Returns:
            Generated password string
        """
        chars = string.ascii_letters + string.digits
        if include_symbols:
            chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
        
        # Ensure at least one of each type
        password = [
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.digits),
        ]
        
        if include_symbols:
            password.append(secrets.choice("!@#$%^&*()-_=+"))
        
        # Fill remaining length
        password.extend(secrets.choice(chars) for _ in range(length - len(password)))
        
        # Shuffle
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    async def authenticate(self, email: str, master_password: str) -> bool:
        """
        Authenticate with Vaultwarden and obtain access token.
        
        Args:
            email: User email
            master_password: Master password
        
        Returns:
            True if authentication successful
        """
        try:
            response = await self.client.post(
                f"{self.vault_url}/identity/connect/token",
                data={
                    "grant_type": "password",
                    "username": email,
                    "password": master_password,
                    "scope": "api offline_access",
                    "client_id": "vertex-genesis",
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                logger.info("✅ Authenticated with Vaultwarden")
                return True
            else:
                logger.error(f"❌ Vaultwarden auth failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Vaultwarden auth error: {e}")
            return False
    
    async def create_cipher(
        self,
        name: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        uri: Optional[str] = None,
        notes: Optional[str] = None,
        folder_id: Optional[str] = None,
        auto_generate_password: bool = False
    ) -> Dict:
        """
        Create a new cipher (credential entry) in Vaultwarden.
        
        Args:
            name: Credential name/title
            username: Username or email
            password: Password (or None to auto-generate)
            uri: Associated URL
            notes: Additional notes
            folder_id: Folder ID for organization
            auto_generate_password: Generate password if not provided
        
        Returns:
            Created cipher data
        """
        if not self.access_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        # Auto-generate password if requested or not provided
        if auto_generate_password or password is None:
            password = self.generate_password()
            logger.info(f"🔑 Generated password for: {name}")
        
        cipher_data = {
            "type": 1,  # Login type
            "name": name,
            "notes": notes or f"Created by Vertex Genesis on {datetime.now().isoformat()}",
            "favorite": False,
            "login": {
                "username": username,
                "password": password,
                "totp": None,
            },
            "fields": [],
            "passwordHistory": []
        }
        
        if uri:
            cipher_data["login"]["uris"] = [{"uri": uri, "match": None}]
        
        if folder_id:
            cipher_data["folderId"] = folder_id
        
        try:
            response = await self.client.post(
                f"{self.vault_url}/api/ciphers",
                json=cipher_data,
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f"✅ Cipher created: {name}")
                return {
                    "id": result.get("Id"),
                    "name": name,
                    "username": username,
                    "password": password,
                    "uri": uri,
                    "created": True
                }
            else:
                logger.error(f"❌ Cipher creation failed: {response.status_code} - {response.text}")
                return {"created": False, "error": response.text}
        except Exception as e:
            logger.error(f"❌ Cipher creation error: {e}")
            return {"created": False, "error": str(e)}
    
    async def get_cipher(self, cipher_id: str) -> Optional[Dict]:
        """
        Retrieve a cipher by ID.
        
        Args:
            cipher_id: Cipher ID
        
        Returns:
            Cipher data or None
        """
        if not self.access_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        try:
            response = await self.client.get(
                f"{self.vault_url}/api/ciphers/{cipher_id}",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Cipher retrieval failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ Cipher retrieval error: {e}")
            return None
    
    async def list_ciphers(self) -> List[Dict]:
        """
        List all ciphers for the authenticated user.
        
        Returns:
            List of cipher data
        """
        if not self.access_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        try:
            response = await self.client.get(
                f"{self.vault_url}/api/ciphers",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("Data", [])
            else:
                logger.error(f"❌ Cipher list failed: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"❌ Cipher list error: {e}")
            return []
    
    async def search_ciphers(self, query: str) -> List[Dict]:
        """
        Search ciphers by name or username.
        
        Args:
            query: Search query
        
        Returns:
            Matching ciphers
        """
        ciphers = await self.list_ciphers()
        query_lower = query.lower()
        
        return [
            c for c in ciphers
            if query_lower in c.get("Name", "").lower() or
               query_lower in c.get("Login", {}).get("Username", "").lower()
        ]
    
    async def delete_cipher(self, cipher_id: str) -> bool:
        """
        Delete a cipher by ID.
        
        Args:
            cipher_id: Cipher ID
        
        Returns:
            True if deleted successfully
        """
        if not self.access_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        try:
            response = await self.client.delete(
                f"{self.vault_url}/api/ciphers/{cipher_id}",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code in [200, 204]:
                logger.info(f"✅ Cipher deleted: {cipher_id}")
                return True
            else:
                logger.error(f"❌ Cipher deletion failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Cipher deletion error: {e}")
            return False
    
    async def create_api_key_cipher(
        self,
        service_name: str,
        api_key: str,
        api_url: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Create a cipher specifically for API keys.
        
        Args:
            service_name: Service name (e.g., "OpenAI", "Anthropic")
            api_key: API key value
            api_url: API base URL
            notes: Additional notes
        
        Returns:
            Created cipher data
        """
        return await self.create_cipher(
            name=f"{service_name} API Key",
            username=service_name,
            password=api_key,
            uri=api_url,
            notes=notes or f"API key for {service_name}",
            auto_generate_password=False
        )
    
    async def create_database_cipher(
        self,
        db_name: str,
        db_host: str,
        db_user: str,
        db_password: Optional[str] = None,
        db_port: int = 5432
    ) -> Dict:
        """
        Create a cipher for database credentials.
        
        Args:
            db_name: Database name
            db_host: Database host
            db_user: Database username
            db_password: Database password (auto-generated if None)
            db_port: Database port
        
        Returns:
            Created cipher data with generated password
        """
        return await self.create_cipher(
            name=f"Database: {db_name}",
            username=db_user,
            password=db_password,
            uri=f"postgresql://{db_host}:{db_port}/{db_name}",
            notes=f"Database credentials for {db_name}",
            auto_generate_password=True
        )
    
    def generate_2fa_secret(self) -> str:
        """
        Generate a base32-encoded secret for 2FA/TOTP.
        Compatible with Google Authenticator, Authy, etc.
        
        Returns:
            Base32-encoded secret (32 characters)
        """
        import base64
        
        # Generate 20 random bytes
        random_bytes = secrets.token_bytes(20)
        
        # Encode to base32 (standard for TOTP)
        secret = base64.b32encode(random_bytes).decode('utf-8')
        
        logger.info("🔐 Generated 2FA secret")
        return secret
    
    def generate_totp_uri(
        self,
        secret: str,
        account_name: str,
        issuer: str = "Vertex Genesis"
    ) -> str:
        """
        Generate a TOTP URI for QR code generation.
        
        Args:
            secret: Base32-encoded secret
            account_name: Account identifier
            issuer: Service name
        
        Returns:
            otpauth:// URI
        """
        from urllib.parse import quote
        
        uri = f"otpauth://totp/{quote(issuer)}:{quote(account_name)}?secret={secret}&issuer={quote(issuer)}"
        return uri
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Singleton instance
vault_manager = VaultManager()
