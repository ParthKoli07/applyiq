"""
analytics.py
------------
Analytics module for ApplyIQ.
Generates insights and statistics from application data.

Author: Parth Koli
Project: ApplyIQ - Smart Internship Application Manager
"""

import pandas as pd
from datetime import datetime, date

def get_application_stats(applications):
    """Generate stats from list of applications"""
    if not applications:
        return {
            'total': 0,
            'applied': 0,
            'interviewing': 0,
            'offered': 0,
            'rejected': 0,
            'success_rate': 0.0,
            'response_rate': 0.0
        }
    
    df = pd.DataFrame(applications)
    
    total = len(df)
    applied = len(df[df['status'] == 'Applied'])
    interviewing = len(df[df['status'] == 'Interview Scheduled'])
    offered = len(df[df['status'] == 'Offered'])
    rejected = len(df[df['status'] == 'Rejected'])
    
    success_rate = round((offered / total) * 100, 1) if total > 0 else 0.0
    response_rate = round(((interviewing + offered + rejected) / total) * 100, 1) if total > 0 else 0.0
    
    return {
        'total': total,
        'applied': applied,
        'interviewing': interviewing,
        'offered': offered,
        'rejected': rejected,
        'success_rate': success_rate,
        'response_rate': response_rate
    }

def get_applications_by_status(applications):
    """Get count of applications by status"""
    if not applications:
        return {}
    
    df = pd.DataFrame(applications)
    return df['status'].value_counts().to_dict()

def get_top_companies(applications, n=5):
    """Get most applied to companies"""
    if not applications:
        return []
    
    df = pd.DataFrame(applications)
    return df['company'].value_counts().head(n).to_dict()

def get_applications_over_time(applications):
    """Get application count over time"""
    if not applications:
        return pd.DataFrame()
    
    df = pd.DataFrame(applications)
    df['applied_date'] = pd.to_datetime(df['applied_date'])
    daily_counts = df.groupby('applied_date').size().reset_index(name='count')
    return daily_counts

def get_follow_up_reminders(applications):
    """Get applications that need follow up today or are overdue"""
    if not applications:
        return []
    
    today = date.today()
    reminders = []
    
    for app in applications:
        if app.get('follow_up_date') and app['status'] == 'Applied':
            follow_up = datetime.strptime(str(app['follow_up_date']), '%Y-%m-%d').date()
            if follow_up <= today:
                days_overdue = (today - follow_up).days
                reminders.append({
                    'company': app['company'],
                    'role': app['role'],
                    'follow_up_date': app['follow_up_date'],
                    'days_overdue': days_overdue
                })
    
    return reminders