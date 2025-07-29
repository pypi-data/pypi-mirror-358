"""
Firebase Admin Helper Functions

This module provides utility functions for managing Firebase Auth users and permissions.
These functions are designed for admin operations and testing purposes.
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
import firebase_admin
from firebase_admin import auth
from ipulse_shared_base_ftredge import log_info, log_warning, log_error, log_debug, LogLevel


def get_user_auth_token(
    email: str, 
    password: str, 
    api_key: str, 
    logger: Optional[logging.Logger] = None, 
    print_out: bool = False,
    debug: bool = False
) -> Optional[str]:
    """
    Get a user authentication token using the Firebase REST API.
    
    Args:
        email: User email
        password: User password
        api_key: Firebase API key
        logger: Optional logger instance
        print_out: Whether to print output
        debug: Whether to print detailed debug info
        
    Returns:
        ID token or None if failed
    """
    import requests  # Import here to keep it optional
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        if debug:
            log_info(f"Sending authentication request to: {url}", logger=logger, print_out=print_out)
            log_info(f"Request payload: {payload}", logger=logger, print_out=print_out)
            
        response = requests.post(url, json=payload)
        
        # Add detailed error logging
        if not response.ok:
            error_details = response.text
            try:
                error_json = response.json()
                if "error" in error_json:
                    error_details = f"{error_json['error'].get('message', 'Unknown error')}"
            except Exception:
                pass
                
            log_error(f"Auth error ({response.status_code}): {error_details}", logger=logger, print_out=print_out)
            
            # Check for specific error conditions
            if "EMAIL_NOT_FOUND" in error_details or "INVALID_PASSWORD" in error_details:
                log_error(f"Authentication failed - invalid credentials for {email}", logger=logger, print_out=print_out)
            elif "USER_DISABLED" in error_details:
                log_error(f"User account is disabled: {email}", logger=logger, print_out=print_out)
            elif "INVALID_EMAIL" in error_details:
                log_error(f"Invalid email format: {email}", logger=logger, print_out=print_out)
            
            return None
        
        token = response.json().get("idToken")
        log_info(f"Successfully obtained auth token for {email}", logger=logger, print_out=print_out)
        return token
    except Exception as e:
        log_error(f"Error getting auth token: {e}", logger=logger, print_out=print_out)
        return None

def list_users(max_results: int = 1000, logger: Optional[logging.Logger] = None, print_out: bool = False) -> List[Dict[str, Any]]:
    """
    List users from Firebase Auth.
    
    Args:
        max_results: Maximum number of users to return
        logger: Optional logger instance
        print_out: Whether to print output
        
    Returns:
        List of user dicts
    """
    try:
        users = []
        page = auth.list_users()
        for user in page.users:
            users.append(user._data)
            if len(users) >= max_results:
                break
        
        log_info(f"Listed {len(users)} users from Firebase Auth", logger=logger, print_out=print_out)
        return users
    except Exception as e:
        log_error(f"Error listing users: {e}", logger=logger, print_out=print_out)
        return []

def create_custom_token(
    user_uid: str, 
    additional_claims: Dict[str, Any] = None, 
    logger: Optional[logging.Logger] = None, 
    print_out: bool = False
) -> str:
    """
    Create a custom token for a user.
    
    Args:
        user_uid: User's UID
        additional_claims: Additional claims to include in the token
        logger: Optional logger instance
        print_out: Whether to print output
        
    Returns:
        Custom token
    """
    try:
        token = auth.create_custom_token(user_uid, additional_claims)
        log_debug(f"Created custom token for user {user_uid}", logger=logger, print_out=print_out)
        return token
    except Exception as e:
        log_error(f"Error creating custom token: {e}", logger=logger, print_out=print_out)
        raise

def verify_id_token(
    token: str, 
    check_revoked: bool = False, 
    logger: Optional[logging.Logger] = None, 
    print_out: bool = False
) -> Dict[str, Any]:
    """
    Verify an ID token.
    
    Args:
        token: ID token to verify
        check_revoked: Whether to check if the token has been revoked
        logger: Optional logger instance
        print_out: Whether to print output
        
    Returns:
        Token claims
    """
    try:
        claims = auth.verify_id_token(token, check_revoked=check_revoked)
        log_debug(f"Verified ID token for user {claims.get('uid')}", logger=logger, print_out=print_out)
        return claims
    except Exception as e:
        log_error(f"Error verifying ID token: {e}", logger=logger, print_out=print_out)
        raise