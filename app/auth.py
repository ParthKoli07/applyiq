"""
auth.py
-------
Authentication module for ApplyIQ.
Handles user signup, login, and session management using Supabase.

Author: Parth Koli
Project: ApplyIQ - Smart Internship Application Manager
"""

import bcrypt
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def signup_user(username, email, password, college=""):
    """Register a new user"""
    try:
        supabase = get_client()
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        existing = supabase.table('users').select('id').eq('username', username).execute()
        if existing.data:
            return False, "Username already exists!"
        
        existing_email = supabase.table('users').select('id').eq('email', email).execute()
        if existing_email.data:
            return False, "Email already exists!"
        
        supabase.table('users').insert({
            'username': username,
            'email': email,
            'password': hashed,
            'college': college
        }).execute()
        
        return True, "Account created successfully!"
    except Exception as e:
        return False, str(e)

def login_user(username, password):
    """Authenticate a user"""
    try:
        supabase = get_client()
        result = supabase.table('users').select('id, username, password, college').eq('username', username).execute()
        
        if not result.data:
            return False, "Invalid username or password!"
        
        user = result.data[0]
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return True, {"id": user['id'], "username": user['username'], "college": user['college']}
        
        return False, "Invalid username or password!"
    except Exception as e:
        return False, str(e)