"""
tracker.py
----------
Application tracking module for ApplyIQ.
Handles CRUD operations for internship applications.

Author: Parth Koli
Project: ApplyIQ - Smart Internship Application Manager
"""

import os
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def add_application(user_id, company, role, jd_text="", 
                     original_resume="", tailored_resume="",
                     status="Applied", applied_date=None,
                     follow_up_date=None, notes=""):
    """Add a new job application"""
    try:
        supabase = get_client()
        data = {
            'user_id': user_id,
            'company': company,
            'role': role,
            'jd_text': jd_text,
            'original_resume': original_resume,
            'tailored_resume': tailored_resume,
            'status': status,
            'notes': notes
        }
        if applied_date:
            data['applied_date'] = str(applied_date)
        if follow_up_date:
            data['follow_up_date'] = str(follow_up_date)
            
        supabase.table('applications').insert(data).execute()
        return True, "Application added successfully!"
    except Exception as e:
        return False, str(e)

def get_applications(user_id):
    """Get all applications for a user"""
    try:
        supabase = get_client()
        result = supabase.table('applications').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return result.data
    except Exception as e:
        print(f"Error fetching applications: {e}")
        return []

def update_application_status(app_id, status):
    """Update application status"""
    try:
        supabase = get_client()
        supabase.table('applications').update({'status': status}).eq('id', app_id).execute()
        return True
    except Exception as e:
        return False

def delete_application(app_id):
    """Delete an application"""
    try:
        supabase = get_client()
        supabase.table('applications').delete().eq('id', app_id).execute()
        return True
    except Exception as e:
        return False