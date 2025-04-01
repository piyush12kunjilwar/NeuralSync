import random
import datetime

def get_device_list():
    """
    Returns a list of supported wearable devices/platforms.
    
    Returns:
        List of device names
    """
    return [
        "Apple Watch",
        "Fitbit",
        "Garmin",
        "Samsung Galaxy Watch",
        "Oura Ring",
        "Whoop",
        "Google Pixel Watch",
        "Apple HealthKit",
        "Google Fit",
        "Other"
    ]

def get_available_data_types(data_source):
    """
    Returns available data types from the specified wearable data source.
    
    Args:
        data_source: String specifying the data source (Apple HealthKit, Google Fit, etc.)
        
    Returns:
        List of available data types
    """
    # In a real app, this would query the actual API to find available data types
    # For demo purposes, return standard metrics based on source
    
    common_metrics = [
        "Heart Rate", 
        "Sleep Data", 
        "Steps", 
        "Active Calories", 
        "Activity Minutes"
    ]
    
    # Health and fitness metrics
    health_metrics = {
        "Apple Watch": ["Heart Rate Variability", "ECG", "Blood Oxygen", "Respiratory Rate", "Cardio Fitness", "Walking Steadiness"],
        "Apple HealthKit": ["Heart Rate Variability", "ECG", "Blood Oxygen", "Respiratory Rate", "Cardio Fitness", "Walking Steadiness", "Mindful Minutes"],
        "Fitbit": ["Resting Heart Rate", "Sleep Stages", "Floors Climbed", "Active Zone Minutes", "Skin Temperature"],
        "Garmin": ["Stress Level", "Body Battery", "Training Status", "VO2 Max", "Sleep Tracking", "Respiration"],
        "Samsung Galaxy Watch": ["Blood Pressure", "ECG", "Body Composition", "Stress Level", "Sleep Tracking"],
        "Oura Ring": ["Readiness Score", "Sleep Quality", "Body Temperature", "Respiratory Rate", "HRV Balance"],
        "Whoop": ["Recovery Score", "Strain Score", "Sleep Performance", "Respiratory Rate", "HRV"],
        "Google Pixel Watch": ["Cardio Load", "Daily Readiness", "Activity Goals", "Stress Tracking"],
        "Google Fit": ["Move Minutes", "Heart Points", "Distance", "Pace", "Calories"]
    }
    
    # Return device-specific metrics
    if data_source in health_metrics:
        return common_metrics + health_metrics[data_source]
    else:
        return common_metrics

def get_mock_wearable_data(date, metrics):
    """
    Generate simulated wearable data for demo purposes.
    
    Args:
        date: String date in format YYYY-MM-DD
        metrics: List of metrics to include
        
    Returns:
        Dictionary of simulated data
    """
    # Create a base data dictionary
    data = {
        'date': date
    }
    
    # Generate appropriate mock data based on selected metrics
    if "Heart Rate" in metrics:
        data['avg_heart_rate'] = random.randint(65, 85)
        data['resting_heart_rate'] = random.randint(55, 75)
        
    if "Heart Rate Variability" in metrics:
        data['heart_rate_variability'] = random.randint(25, 65)
    
    if "Sleep Data" in metrics:
        data['sleep_hours'] = round(random.uniform(5.5, 8.5), 2)
        data['deep_sleep_percentage'] = random.randint(15, 30)
        data['rem_sleep_percentage'] = random.randint(20, 30)
        data['sleep_disruptions'] = random.randint(0, 5)
    
    if "Steps" in metrics:
        data['steps'] = random.randint(3000, 12000)
    
    if "Active Calories" in metrics:
        data['active_calories'] = random.randint(100, 500)
    
    if "Activity Minutes" in metrics:
        data['activity_minutes'] = random.randint(10, 120)
        
    # Add the new metrics
    if "Blood Oxygen" in metrics:
        data['blood_oxygen'] = random.randint(95, 100)
        
    if "Respiratory Rate" in metrics:
        data['respiratory_rate'] = random.randint(12, 20)
        
    if "ECG" in metrics:
        data['ecg_normal'] = random.random() > 0.1  # 90% chance of normal ECG
        
    if "Stress Level" in metrics or "Stress Score" in metrics:
        data['stress_score'] = random.randint(1, 100)
        
    if "Body Battery" in metrics:
        data['body_battery'] = random.randint(5, 100)
        
    if "VO2 Max" in metrics or "Cardio Fitness" in metrics:
        data['vo2_max'] = random.randint(30, 60)
        
    if "Training Status" in metrics:
        statuses = ["Productive", "Maintaining", "Recovery", "Detraining", "Peaking"]
        data['training_status'] = random.choice(statuses)
        
    if "Sleep Quality" in metrics or "Sleep Tracking" in metrics or "Sleep Stages" in metrics:
        if 'sleep_hours' not in data:  # If sleep data wasn't already added
            data['sleep_hours'] = round(random.uniform(5.5, 8.5), 2)
            data['deep_sleep_percentage'] = random.randint(15, 30)
            data['rem_sleep_percentage'] = random.randint(20, 30)
        data['sleep_quality_score'] = random.randint(1, 100)
        
    if "Body Temperature" in metrics or "Skin Temperature" in metrics:
        data['body_temp'] = round(random.uniform(36.1, 37.0), 1)
        
    if "Recovery Score" in metrics or "Readiness Score" in metrics:
        data['recovery_score'] = random.randint(1, 100)
        
    if "Strain Score" in metrics:
        data['strain_score'] = random.randint(1, 21)  # WHOOP uses 1-21 scale
        
    if "Blood Pressure" in metrics:
        data['systolic'] = random.randint(100, 140)
        data['diastolic'] = random.randint(60, 90)
        
    if "Body Composition" in metrics:
        data['body_fat_percentage'] = round(random.uniform(10, 30), 1)
        data['muscle_mass'] = round(random.uniform(25, 45), 1)
        
    if "Mindful Minutes" in metrics:
        data['mindful_minutes'] = random.randint(0, 60)
        
    if "Floors Climbed" in metrics:
        data['floors_climbed'] = random.randint(0, 30)
        
    if "Distance" in metrics:
        data['distance_km'] = round(random.uniform(0.5, 10), 2)
        
    if "Active Zone Minutes" in metrics or "Heart Points" in metrics:
        data['active_zone_minutes'] = random.randint(0, 90)
    
    # Add some variation based on the date (weekend vs weekday)
    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
    is_weekend = date_obj.weekday() >= 5  # 5=Saturday, 6=Sunday
    
    if is_weekend:
        # More sleep and activity on weekends
        if 'sleep_hours' in data:
            data['sleep_hours'] += random.uniform(0.5, 1.0)
        if 'steps' in data:
            data['steps'] += random.randint(1000, 3000)
        if 'activity_minutes' in data:
            data['activity_minutes'] += random.randint(20, 45)
        if 'mindful_minutes' in data:
            data['mindful_minutes'] += random.randint(10, 20)
    
    return data

def connect_to_health_api(api_name, credentials=None):
    """
    In a real application, this function would connect to the specified health API.
    For this demo, it returns a mock success message.
    
    Args:
        api_name: String specifying which API to connect to
        credentials: Any required authentication credentials
        
    Returns:
        Boolean indicating success and a message
    """
    # In a real app, this would attempt to authenticate with the API
    # and retrieve actual user data
    
    return True, f"Successfully connected to {api_name}. Ready to import data."

def get_real_time_heart_rate():
    """
    In a real app, this would connect to a wearable device's real-time API.
    For demo, returns simulated real-time heart rate.
    
    Returns:
        Dictionary with heart rate data
    """
    # Simulate heart rate with small random variations
    return {
        'current': random.randint(65, 85),
        'timestamp': datetime.datetime.now().isoformat(),
        'is_elevated': random.random() > 0.8  # 20% chance of elevated HR
    }

def get_real_time_metrics(device_type, metrics=None):
    """
    Gets real-time metrics from wearable devices.
    In a real app, this would connect to the device's real-time API.
    
    Args:
        device_type: String specifying the device (Apple Watch, Fitbit, etc.)
        metrics: List of metrics to retrieve (if None, gets all available)
        
    Returns:
        Dictionary with real-time health metrics
    """
    if metrics is None:
        # Default set of real-time metrics that most devices can provide
        metrics = ["Heart Rate", "Steps"]
        
        # Add device-specific metrics if available
        if device_type in ["Apple Watch", "Garmin", "Whoop"]:
            metrics.append("Heart Rate Variability")
        if device_type in ["Apple Watch", "Fitbit", "Samsung Galaxy Watch"]:
            metrics.append("Blood Oxygen")
        if device_type in ["Garmin", "Whoop"]:
            metrics.append("Stress Level")
    
    # Create base data structure
    data = {
        'timestamp': datetime.datetime.now().isoformat(),
        'device': device_type
    }
    
    # Add metrics data
    if "Heart Rate" in metrics:
        # Simulate a realistic heart rate with small variations
        data['heart_rate'] = random.randint(65, 85)
        data['heart_rate_zone'] = categorize_heart_rate_zone(data['heart_rate'])
    
    if "Heart Rate Variability" in metrics:
        data['hrv'] = random.randint(25, 65)
    
    if "Blood Oxygen" in metrics:
        data['blood_oxygen'] = random.randint(95, 100)
    
    if "Steps" in metrics:
        # Assume steps accumulate throughout the day
        current_hour = datetime.datetime.now().hour
        # More steps during active hours (8am-8pm)
        if 8 <= current_hour <= 20:
            # Calculate a reasonable step count for the current time of day
            expected_daily_steps = random.randint(7000, 10000)
            progress_through_day = (current_hour - 8) / 12  # 0 to 1 scale for 8am-8pm
            data['steps'] = int(expected_daily_steps * min(1, max(0, progress_through_day)))
        else:
            # Minimal steps during night hours
            data['steps'] = random.randint(0, 500)
    
    if "Stress Level" in metrics:
        data['stress_level'] = random.randint(1, 100)
        data['stress_category'] = categorize_stress_level(data['stress_level'])
    
    if "Respiratory Rate" in metrics:
        data['respiratory_rate'] = random.randint(12, 20)
    
    if "Calories" in metrics or "Active Calories" in metrics:
        # Similar to steps, calories accumulate throughout the day
        current_hour = datetime.datetime.now().hour
        if 8 <= current_hour <= 20:
            expected_daily_calories = random.randint(300, 600)
            progress_through_day = (current_hour - 8) / 12
            data['active_calories'] = int(expected_daily_calories * min(1, max(0, progress_through_day)))
        else:
            data['active_calories'] = random.randint(0, 50)
    
    return data

def categorize_heart_rate_zone(heart_rate):
    """
    Categorize heart rate into training zones.
    
    Args:
        heart_rate: Current heart rate in BPM
        
    Returns:
        String indicating heart rate zone
    """
    # Using a simplified version of heart rate zones based on percent of max HR
    # Assuming a max HR of 220 - 30 (age) = 190 for a 30-year-old
    max_hr = 190
    
    percent_of_max = (heart_rate / max_hr) * 100
    
    if percent_of_max < 50:
        return "Rest"
    elif percent_of_max < 60:
        return "Very Light"
    elif percent_of_max < 70:
        return "Light"
    elif percent_of_max < 80:
        return "Moderate"
    elif percent_of_max < 90:
        return "Hard"
    else:
        return "Maximum"

def categorize_stress_level(stress_score):
    """
    Categorize a stress score into descriptive categories.
    
    Args:
        stress_score: Numeric stress score (1-100)
        
    Returns:
        String indicating stress category
    """
    if stress_score < 25:
        return "Low"
    elif stress_score < 50:
        return "Normal"
    elif stress_score < 75:
        return "Elevated"
    else:
        return "High"
