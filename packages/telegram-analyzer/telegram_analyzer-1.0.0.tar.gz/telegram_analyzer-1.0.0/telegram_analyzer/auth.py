"""
Authentication module for Telegram Analyzer.
This module provides user authentication functionality.
"""

import os
import json
import hashlib
import secrets
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

# User database file path
DEFAULT_USER_DB = "users.json"

class Auth:
    """Authentication manager for Telegram Analyzer"""
    
    def __init__(self, user_db_path: str = DEFAULT_USER_DB):
        """
        Initialize authentication manager.
        
        Args:
            user_db_path: Path to user database JSON file
        """
        self.user_db_path = user_db_path
        self.logger = logging.getLogger(__name__)
        self.sessions = {}  # In-memory session storage
        self._load_users()
        
    def _load_users(self):
        """Load users from database file"""
        try:
            if os.path.exists(self.user_db_path):
                with open(self.user_db_path, 'r') as f:
                    self.users = json.load(f)
            else:
                self.users = {}
                self._save_users()  # Create empty database file
                
            self.logger.info(f"Loaded {len(self.users)} users from database")
        except Exception as e:
            self.logger.error(f"Error loading user database: {str(e)}")
            self.users = {}
    
    def _save_users(self):
        """Save users to database file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(self.user_db_path)), exist_ok=True)
            
            with open(self.user_db_path, 'w') as f:
                json.dump(self.users, f, indent=2)
                
            self.logger.info(f"Saved {len(self.users)} users to database")
        except Exception as e:
            self.logger.error(f"Error saving user database: {str(e)}")
    
    def register_user(self, username: str, password: str, email: str = None) -> Tuple[bool, str]:
        """
        Register a new user.
        
        Args:
            username: Username
            password: Password
            email: Email address (optional)
            
        Returns:
            Tuple of (success, message)
        """
        # Validate username
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        # Check if username already exists
        if username.lower() in [u.lower() for u in self.users.keys()]:
            return False, "Username already exists"
        
        # Validate password
        if not password or len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        # Create password hash
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)
        
        # Create user
        self.users[username] = {
            'password_hash': password_hash,
            'salt': salt,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        
        # Save to database
        self._save_users()
        
        return True, "User registered successfully"
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """
        Authenticate a user.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Tuple of (success, message, session_id)
        """
        # Check if user exists
        if username not in self.users:
            return False, "Invalid username or password", None
        
        # Get user
        user = self.users[username]
        
        # Verify password
        if self._hash_password(password, user['salt']) != user['password_hash']:
            return False, "Invalid username or password", None
        
        # Update last login
        user['last_login'] = datetime.now().isoformat()
        self._save_users()
        
        # Create session
        session_id = secrets.token_hex(32)
        self.sessions[session_id] = {
            'username': username,
            'expires': datetime.now() + timedelta(hours=24)
        }
        
        return True, "Authentication successful", session_id
    
    def verify_session(self, session_id: str) -> Tuple[bool, Optional[str]]:
        """
        Verify a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Tuple of (valid, username)
        """
        if not session_id or session_id not in self.sessions:
            return False, None
            
        session = self.sessions[session_id]
        
        # Check if session has expired
        if datetime.now() > session['expires']:
            # Remove expired session
            del self.sessions[session_id]
            return False, None
            
        return True, session['username']
    
    def logout(self, session_id: str) -> bool:
        """
        Log out a user by invalidating their session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if session was found and removed, False otherwise
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def change_password(self, username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Change a user's password.
        
        Args:
            username: Username
            old_password: Current password
            new_password: New password
            
        Returns:
            Tuple of (success, message)
        """
        # Check if user exists
        if username not in self.users:
            return False, "User not found"
        
        # Get user
        user = self.users[username]
        
        # Verify old password
        if self._hash_password(old_password, user['salt']) != user['password_hash']:
            return False, "Incorrect current password"
        
        # Validate new password
        if not new_password or len(new_password) < 6:
            return False, "New password must be at least 6 characters"
        
        # Update password
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(new_password, salt)
        
        user['password_hash'] = password_hash
        user['salt'] = salt
        
        # Save to database
        self._save_users()
        
        return True, "Password changed successfully"
    
    def delete_user(self, username: str) -> Tuple[bool, str]:
        """
        Delete a user.
        
        Args:
            username: Username
            
        Returns:
            Tuple of (success, message)
        """
        if username not in self.users:
            return False, "User not found"
        
        # Remove user
        del self.users[username]
        
        # Remove any active sessions for this user
        for session_id, session in list(self.sessions.items()):
            if session['username'] == username:
                del self.sessions[session_id]
        
        # Save to database
        self._save_users()
        
        return True, "User deleted successfully"
    
    def _hash_password(self, password: str, salt: str) -> str:
        """
        Hash a password with a salt.
        
        Args:
            password: Password to hash
            salt: Salt to use
            
        Returns:
            Hashed password
        """
        # Combine password and salt
        salted = password + salt
        
        # Hash using SHA-256
        return hashlib.sha256(salted.encode()).hexdigest()

def get_auth_handler(user_db_path: str = DEFAULT_USER_DB) -> Auth:
    """
    Get an Auth instance.
    
    Args:
        user_db_path: Path to user database JSON file
        
    Returns:
        Auth instance
    """
    return Auth(user_db_path)
