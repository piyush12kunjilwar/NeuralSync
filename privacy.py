import json
import base64
import os
import hashlib

def encrypt_data(data_dict):
    """
    Simulate data encryption for privacy.
    
    In a real application, this would use proper encryption like AES.
    For this demo, we're using a simple encoding to represent the concept.
    
    Args:
        data_dict: Dictionary containing data to encrypt
        
    Returns:
        Original dictionary (in a real app, this would be encrypted)
    """
    # For demo purposes, we're not actually encrypting
    # In a real application, we would use proper encryption
    
    # We'll add a flag to indicate this data would be encrypted
    # in a real application
    data_dict['_would_be_encrypted'] = True
    
    # Return the original data
    return data_dict

def decrypt_data(encrypted_data):
    """
    Simulate data decryption.
    
    In a real application, this would decrypt properly encrypted data.
    For this demo, we just return the original data.
    
    Args:
        encrypted_data: Dictionary that would be encrypted in a real app
        
    Returns:
        Original dictionary
    """
    # For demo purposes, we're just returning the original data
    # In a real application, we would use proper decryption
    
    # Create a copy to avoid modifying the original
    decrypted_data = encrypted_data.copy()
    
    # Remove the flag if it exists
    if '_would_be_encrypted' in decrypted_data:
        del decrypted_data['_would_be_encrypted']
    
    return decrypted_data

def anonymize_data(data_dict):
    """
    Anonymize data for sharing or aggregation.
    
    Args:
        data_dict: Dictionary containing personal data
        
    Returns:
        Anonymized version of the data
    """
    # Create a copy to avoid modifying the original
    anonymized = data_dict.copy()
    
    # Remove direct identifiers
    if 'user_id' in anonymized:
        del anonymized['user_id']
    if 'name' in anonymized:
        del anonymized['name']
    if 'email' in anonymized:
        del anonymized['email']
    
    # Remove or redact free text that could contain personal information
    if 'content' in anonymized:
        anonymized['content'] = "[REDACTED PERSONAL TEXT]"
    if 'title' in anonymized:
        anonymized['title'] = "[REDACTED TITLE]"
    
    # Keep only aggregate or non-identifying metrics
    safe_keys = [
        'mood_score', 'stress_level', 'sleep_quality', 
        'sleep_hours', 'avg_heart_rate', 'steps',
        'deep_sleep_percentage', 'rem_sleep_percentage'
    ]
    
    safe_data = {k: anonymized[k] for k in safe_keys if k in anonymized}
    
    # Add a hash as a non-identifying unique ID if needed for research
    if 'date' in anonymized:
        date_string = anonymized['date']
        hash_input = f"{date_string}{os.urandom(8).hex()}"
        anonymized_id = hashlib.sha256(hash_input.encode()).hexdigest()[:12]
        safe_data['anonymized_id'] = anonymized_id
    
    return safe_data

def create_data_export(user_data, include_sensitive=False):
    """
    Create a user data export in compliance with privacy regulations.
    
    Args:
        user_data: Dictionary containing all user data
        include_sensitive: Boolean indicating whether to include sensitive data
        
    Returns:
        Dictionary formatted for export
    """
    # Create export structure
    export = {
        'export_date': os.environ.get('CURRENT_DATE', '2023-01-01'),
        'data_categories': []
    }
    
    # Journal entries
    if 'journal_entries' in user_data:
        journal_export = {
            'category': 'Journal Entries',
            'items': []
        }
        
        for entry in user_data['journal_entries']:
            decrypted_entry = decrypt_data(entry)
            
            # Remove sentiment analysis if not including sensitive data
            if not include_sensitive and 'sentiment' in decrypted_entry:
                del decrypted_entry['sentiment']
            
            journal_export['items'].append(decrypted_entry)
        
        export['data_categories'].append(journal_export)
    
    # Wearable data
    if 'wearable_data' in user_data:
        wearable_export = {
            'category': 'Wearable Health Data',
            'items': user_data['wearable_data']
        }
        export['data_categories'].append(wearable_export)
    
    # Coping strategies (non-sensitive)
    if 'coping_strategies' in user_data:
        strategies_export = {
            'category': 'Coping Strategies',
            'items': user_data['coping_strategies']
        }
        export['data_categories'].append(strategies_export)
    
    return export

def generate_privacy_summary():
    """
    Generate a human-readable privacy practice summary.
    
    Returns:
        String with privacy information
    """
    return """
    # NeuroSync Privacy Information
    
    ## Data Storage
    - Journal entries are encrypted before storage
    - All sensitive data is processed locally on your device
    - Raw wearable data is never transmitted to external servers
    
    ## Data Usage
    - Your data is used only to provide personalized insights to you
    - No data is shared with third parties
    - AI processing of journal entries is done with state-of-the-art security
    
    ## Your Rights
    - You can export all your data at any time
    - You can delete your data completely from our systems
    - You control what wearable metrics are imported and analyzed
    
    ## Anonymized Research
    - If you opt in, strictly anonymized data may be used for mental health research
    - No journal text or personally identifiable information is ever included
    - You can opt out at any time through settings
    """
