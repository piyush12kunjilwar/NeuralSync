import json
import os
import datetime
import streamlit as st

def load_user_data(user_id):
    """
    Load user data from simulated storage.
    
    In a real app, this would fetch data from a database or encrypted file.
    For this demo, we'll use Streamlit's session state as persistent storage.
    
    Args:
        user_id: String user identifier
        
    Returns:
        Dictionary with user data or None if not found
    """
    # Initialize storage in session state if not exists
    if 'user_data_store' not in st.session_state:
        st.session_state.user_data_store = {}
    
    # Return user data if exists
    if user_id in st.session_state.user_data_store:
        return st.session_state.user_data_store[user_id]
    
    # If no data found, create an empty structure
    sample_data = create_sample_data(user_id)
    st.session_state.user_data_store[user_id] = sample_data
    return sample_data

def save_user_data(user_id, data):
    """
    Save user data to simulated storage.
    
    Args:
        user_id: String user identifier
        data: Dictionary with user data
        
    Returns:
        Boolean indicating success
    """
    # Initialize storage in session state if not exists
    if 'user_data_store' not in st.session_state:
        st.session_state.user_data_store = {}
    
    # Save data
    st.session_state.user_data_store[user_id] = data
    return True

def validate_date_format(date_str):
    """
    Validate that a string is in YYYY-MM-DD format.
    
    Args:
        date_str: String to validate
        
    Returns:
        Boolean indicating if format is valid
    """
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def format_date(date_obj):
    """
    Format a datetime object as YYYY-MM-DD.
    
    Args:
        date_obj: datetime object
        
    Returns:
        Formatted date string
    """
    return date_obj.strftime("%Y-%m-%d")

def get_date_range(days):
    """
    Get a list of date strings for the last N days.
    
    Args:
        days: Number of days to include
        
    Returns:
        List of date strings in YYYY-MM-DD format
    """
    today = datetime.datetime.now()
    date_list = []
    
    for i in range(days):
        date = today - datetime.timedelta(days=i)
        date_list.append(format_date(date))
    
    return date_list

def create_sample_data(user_id):
    """
    Create minimal sample data for a new user.
    
    Args:
        user_id: String user identifier
        
    Returns:
        Dictionary with basic user data structure
    """
    # Create basic structure
    user_data = {
        'journal_entries': [],
        'wearable_data': [],
        'coping_strategies': []
    }
    
    # Add a welcome strategy
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    welcome_strategy = {
        'date': today,
        'focus_areas': ['Getting Started'],
        'strategy': """
        # Welcome to NeuroSync!
        
        ## Start Your Mental Health Journey
        
        **Steps:**
        1. Begin by adding a journal entry to track your mood
        2. Connect a wearable device to import health data
        3. Explore the dashboard to see your mental health patterns
        4. Generate personalized coping strategies based on your data
        
        **Benefits:** Building self-awareness is the first step toward better mental health.
        
        **Remember:** Consistency is key. Regular check-ins will help you notice patterns and make positive changes.
        """
    }
    
    user_data['coping_strategies'].append(welcome_strategy)
    
    return user_data

def get_streak_days(journal_entries):
    """
    Calculate how many consecutive days a user has journaled.
    
    Args:
        journal_entries: List of journal entry dictionaries
        
    Returns:
        Integer representing consecutive days
    """
    if not journal_entries:
        return 0
    
    # Get list of dates
    dates = [entry.get('date', '') for entry in journal_entries if validate_date_format(entry.get('date', ''))]
    
    if not dates:
        return 0
    
    # Convert to datetime objects
    date_objects = [datetime.datetime.strptime(date, "%Y-%m-%d").date() for date in dates]
    
    # Sort dates (newest first)
    date_objects.sort(reverse=True)
    
    # Check for today
    today = datetime.datetime.now().date()
    if date_objects[0] != today:
        return 0  # Streak broken if no entry today
    
    # Count consecutive days
    streak = 1
    for i in range(len(date_objects) - 1):
        if date_objects[i] - datetime.timedelta(days=1) == date_objects[i+1]:
            streak += 1
        else:
            break
    
    return streak

def filter_data_by_date_range(data_list, start_date, end_date, date_key='date'):
    """
    Filter a list of dictionaries by date range.
    
    Args:
        data_list: List of dictionaries containing date fields
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD)
        date_key: Key in dictionaries that contains the date
        
    Returns:
        Filtered list
    """
    if not data_list:
        return []
    
    # Convert strings to datetime objects
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    
    # Filter the list
    filtered = []
    for item in data_list:
        if date_key in item and validate_date_format(item[date_key]):
            item_date = datetime.datetime.strptime(item[date_key], "%Y-%m-%d").date()
            if start <= item_date <= end:
                filtered.append(item)
    
    return filtered
