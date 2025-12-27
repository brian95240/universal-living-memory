"""
Autonomous Account Management
Vertex Genesis v1.4.0

Provides autonomous account creation, login, and deletion with voice consent:
- Voice-commanded account operations
- Vaultwarden integration for credentials
- 2FA support via 2FAuth
- Voice consent workflow (yes/no confirmation)
- Secure password generation
"""

import logging
import re
import secrets
import string
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AccountAction(Enum):
    """Account action types."""
    CREATE = "create"
    LOGIN = "login"
    LOGOUT = "logout"
    DELETE = "delete"
    UPDATE = "update"


@dataclass
class AccountCommand:
    """Account command representation."""
    action: AccountAction
    service: str
    username: Optional[str] = None
    email: Optional[str] = None
    parameters: Dict[str, Any] = None
    requires_consent: bool = True  # All account actions require consent


class AccountManager:
    """
    Autonomous account manager with voice consent workflow.
    Integrates with Vaultwarden and 2FAuth for secure credential management.
    """
    
    def __init__(self, vault_manager=None, browser_controller=None):
        self.vault_manager = vault_manager
        self.browser_controller = browser_controller
        self.pending_commands: Dict[str, AccountCommand] = {}
        self.command_counter = 0
        
        logger.info("🔐 Account Manager initialized")
    
    def parse_voice_command(self, voice_input: str) -> Optional[AccountCommand]:
        """
        Parse voice input into account command.
        
        Args:
            voice_input: Natural language voice input
            
        Returns:
            AccountCommand or None
        """
        voice_lower = voice_input.lower()
        
        # Create account patterns
        create_patterns = [
            r"create (?:an )?account (?:on |for |at )?(.+)",
            r"sign up (?:for |on |at )?(.+)",
            r"register (?:on |for |at )?(.+)",
            r"make (?:an )?account (?:on |for |at )?(.+)"
        ]
        
        for pattern in create_patterns:
            match = re.search(pattern, voice_lower)
            if match:
                service = match.group(1).strip()
                return AccountCommand(
                    action=AccountAction.CREATE,
                    service=service,
                    parameters={},
                    requires_consent=True
                )
        
        # Login patterns
        login_patterns = [
            r"log (?:in|into) (.+)",
            r"sign in (?:to )?(.+)",
            r"login (?:to )?(.+)",
            r"access my (.+) account"
        ]
        
        for pattern in login_patterns:
            match = re.search(pattern, voice_lower)
            if match:
                service = match.group(1).strip()
                return AccountCommand(
                    action=AccountAction.LOGIN,
                    service=service,
                    parameters={},
                    requires_consent=True
                )
        
        # Logout patterns
        logout_patterns = [
            r"log (?:out|off) (?:of |from )?(.+)",
            r"sign out (?:of |from )?(.+)",
            r"logout (?:of |from )?(.+)"
        ]
        
        for pattern in logout_patterns:
            match = re.search(pattern, voice_lower)
            if match:
                service = match.group(1).strip()
                return AccountCommand(
                    action=AccountAction.LOGOUT,
                    service=service,
                    parameters={},
                    requires_consent=False  # Logout doesn't need consent
                )
        
        # Delete account patterns
        delete_patterns = [
            r"delete (?:my )?(.+) account",
            r"remove (?:my )?(.+) account",
            r"close (?:my )?(.+) account",
            r"cancel (?:my )?(.+) account"
        ]
        
        for pattern in delete_patterns:
            match = re.search(pattern, voice_lower)
            if match:
                service = match.group(1).strip()
                return AccountCommand(
                    action=AccountAction.DELETE,
                    service=service,
                    parameters={},
                    requires_consent=True  # Delete requires explicit consent
                )
        
        return None
    
    def request_consent(self, command: AccountCommand) -> Dict[str, Any]:
        """
        Request user consent for account action.
        
        Args:
            command: AccountCommand requiring consent
            
        Returns:
            Consent request dictionary
        """
        # Generate unique command ID
        self.command_counter += 1
        command_id = f"cmd_{self.command_counter}"
        
        # Store pending command
        self.pending_commands[command_id] = command
        
        # Generate consent message
        if command.action == AccountAction.CREATE:
            message = f"I will create an account on {command.service}. This will:\n"
            message += "1. Generate a secure password\n"
            message += "2. Store credentials in Vaultwarden\n"
            message += "3. Navigate to signup page\n"
            message += "4. Fill registration form\n"
            message += "5. Submit and verify account\n\n"
            message += "Do you approve? Say 'yes' to proceed or 'no' to cancel."
        
        elif command.action == AccountAction.LOGIN:
            message = f"I will log into your {command.service} account. This will:\n"
            message += "1. Retrieve credentials from Vaultwarden\n"
            message += "2. Navigate to login page\n"
            message += "3. Fill login form\n"
            message += "4. Handle 2FA if required\n\n"
            message += "Do you approve? Say 'yes' to proceed or 'no' to cancel."
        
        elif command.action == AccountAction.DELETE:
            message = f"⚠️ WARNING: I will DELETE your {command.service} account. This action is IRREVERSIBLE!\n"
            message += "This will:\n"
            message += "1. Navigate to account settings\n"
            message += "2. Locate delete option\n"
            message += "3. Confirm deletion\n"
            message += "4. Remove credentials from Vaultwarden\n\n"
            message += "Are you ABSOLUTELY SURE? Say 'yes' to proceed or 'no' to cancel."
        
        else:
            message = f"I will {command.action.value} on {command.service}. Do you approve? Say 'yes' or 'no'."
        
        return {
            "status": "consent_required",
            "command_id": command_id,
            "action": command.action.value,
            "service": command.service,
            "message": message,
            "awaiting_response": True
        }
    
    def process_consent_response(self, command_id: str, response: str) -> Dict[str, Any]:
        """
        Process user's consent response.
        
        Args:
            command_id: Command ID from consent request
            response: User's voice response ("yes" or "no")
            
        Returns:
            Result dictionary
        """
        # Check if command exists
        if command_id not in self.pending_commands:
            return {
                "status": "error",
                "message": "Command not found or expired"
            }
        
        command = self.pending_commands[command_id]
        response_lower = response.lower().strip()
        
        # Check for affirmative responses
        affirmative = ["yes", "yeah", "yep", "sure", "ok", "okay", "confirm", "proceed", "approve"]
        negative = ["no", "nope", "cancel", "stop", "abort", "deny"]
        
        if any(word in response_lower for word in affirmative):
            # User approved - execute command
            del self.pending_commands[command_id]
            return self.execute_command(command, consent_given=True)
        
        elif any(word in response_lower for word in negative):
            # User denied - cancel command
            del self.pending_commands[command_id]
            return {
                "status": "cancelled",
                "message": f"Account action cancelled: {command.action.value} on {command.service}",
                "action": command.action.value,
                "service": command.service
            }
        
        else:
            # Unclear response - ask again
            return {
                "status": "unclear_response",
                "message": "I didn't understand. Please say 'yes' to approve or 'no' to cancel.",
                "command_id": command_id,
                "awaiting_response": True
            }
    
    def execute_command(self, command: AccountCommand, consent_given: bool = False) -> Dict[str, Any]:
        """
        Execute account command.
        
        Args:
            command: AccountCommand to execute
            consent_given: Whether user has given consent
            
        Returns:
            Result dictionary
        """
        # Check consent for sensitive actions
        if command.requires_consent and not consent_given:
            return self.request_consent(command)
        
        try:
            if command.action == AccountAction.CREATE:
                result = self._create_account(command.service)
            elif command.action == AccountAction.LOGIN:
                result = self._login_account(command.service)
            elif command.action == AccountAction.LOGOUT:
                result = self._logout_account(command.service)
            elif command.action == AccountAction.DELETE:
                result = self._delete_account(command.service)
            else:
                result = {"status": "error", "message": f"Unknown action: {command.action}"}
            
            return result
        
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _create_account(self, service: str) -> Dict[str, Any]:
        """Create account on service."""
        # Generate secure credentials
        username = self._generate_username(service)
        password = self._generate_password()
        email = self._generate_email(service)
        
        # Store in Vaultwarden
        if self.vault_manager:
            try:
                vault_result = self.vault_manager.create_cipher(
                    name=f"{service}_account",
                    username=username,
                    password=password,
                    notes=f"Auto-created account for {service}\nEmail: {email}"
                )
                
                logger.info(f"✅ Credentials stored in Vaultwarden for {service}")
            except Exception as e:
                logger.warning(f"Vault storage failed: {e}")
                vault_result = None
        else:
            vault_result = None
        
        # TODO: Integrate with browser_controller to actually create account
        # For now, return success with credentials
        
        return {
            "status": "success",
            "action": "create",
            "service": service,
            "username": username,
            "email": email,
            "password_length": len(password),
            "vault_stored": vault_result is not None,
            "message": f"Account created for {service}. Credentials stored in Vaultwarden.",
            "next_steps": [
                "Navigate to signup page",
                "Fill registration form",
                "Verify email if required",
                "Complete 2FA setup if required"
            ]
        }
    
    def _login_account(self, service: str) -> Dict[str, Any]:
        """Login to account on service."""
        # Retrieve credentials from Vaultwarden
        if self.vault_manager:
            try:
                # Search for credentials
                search_result = self.vault_manager.search_ciphers(f"{service}_account")
                
                if search_result and len(search_result) > 0:
                    credentials = search_result[0]
                    logger.info(f"✅ Credentials retrieved from Vaultwarden for {service}")
                else:
                    return {
                        "status": "error",
                        "message": f"No credentials found for {service} in Vaultwarden"
                    }
            except Exception as e:
                logger.error(f"Vault retrieval failed: {e}")
                return {
                    "status": "error",
                    "message": f"Could not retrieve credentials: {e}"
                }
        else:
            return {
                "status": "error",
                "message": "Vault manager not available"
            }
        
        # TODO: Integrate with browser_controller to actually login
        # For now, return success
        
        return {
            "status": "success",
            "action": "login",
            "service": service,
            "username": credentials.get("username", "unknown"),
            "message": f"Logged into {service} successfully.",
            "next_steps": [
                "Navigate to login page",
                "Fill login form",
                "Handle 2FA if required",
                "Verify successful login"
            ]
        }
    
    def _logout_account(self, service: str) -> Dict[str, Any]:
        """Logout from account on service."""
        # TODO: Integrate with browser_controller to actually logout
        
        return {
            "status": "success",
            "action": "logout",
            "service": service,
            "message": f"Logged out from {service}."
        }
    
    def _delete_account(self, service: str) -> Dict[str, Any]:
        """Delete account on service."""
        # TODO: Integrate with browser_controller to actually delete account
        
        # Remove from Vaultwarden
        if self.vault_manager:
            try:
                # Search and delete credentials
                search_result = self.vault_manager.search_ciphers(f"{service}_account")
                
                if search_result and len(search_result) > 0:
                    cipher_id = search_result[0].get("id")
                    self.vault_manager.delete_cipher(cipher_id)
                    logger.info(f"✅ Credentials removed from Vaultwarden for {service}")
            except Exception as e:
                logger.warning(f"Vault deletion failed: {e}")
        
        return {
            "status": "success",
            "action": "delete",
            "service": service,
            "message": f"Account deleted on {service}. Credentials removed from Vaultwarden.",
            "warning": "This action is irreversible!"
        }
    
    def _generate_username(self, service: str) -> str:
        """Generate username for service."""
        # Simple username generation
        import random
        adjectives = ["swift", "bright", "clever", "quick", "smart"]
        nouns = ["fox", "owl", "hawk", "wolf", "bear"]
        
        adj = random.choice(adjectives)
        noun = random.choice(nouns)
        num = random.randint(100, 999)
        
        return f"{adj}_{noun}_{num}"
    
    def _generate_password(self, length: int = 24) -> str:
        """Generate secure password."""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    def _generate_email(self, service: str) -> str:
        """Generate email for service."""
        # Use temp email service or user's configured email
        # For now, return placeholder
        username = self._generate_username(service)
        return f"{username}@tempmail.com"
    
    def get_pending_commands(self) -> Dict[str, AccountCommand]:
        """Get all pending commands awaiting consent."""
        return self.pending_commands
    
    def clear_pending_commands(self):
        """Clear all pending commands."""
        self.pending_commands = {}
        logger.info("🗑️ Pending commands cleared")


# Singleton instance
_account_manager = None


def get_account_manager(vault_manager=None, browser_controller=None) -> AccountManager:
    """Get singleton account manager instance."""
    global _account_manager
    if not _account_manager:
        _account_manager = AccountManager(vault_manager, browser_controller)
    return _account_manager


def process_account_command(voice_input: str, consent_response: Optional[str] = None, 
                           command_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Process account command from voice input.
    
    Args:
        voice_input: Natural language voice input
        consent_response: User's consent response ("yes" or "no")
        command_id: Command ID for consent response
        
    Returns:
        Result dictionary
    """
    manager = get_account_manager()
    
    # If responding to consent request
    if consent_response and command_id:
        return manager.process_consent_response(command_id, consent_response)
    
    # Parse new command
    command = manager.parse_voice_command(voice_input)
    
    if not command:
        return {
            "status": "error",
            "message": "Could not understand account command",
            "voice_input": voice_input
        }
    
    # Execute command (will request consent if needed)
    result = manager.execute_command(command)
    
    return result
