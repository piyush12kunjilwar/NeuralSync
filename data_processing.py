import datetime
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import random

# Try to download NLTK data if not available
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

def process_journal_entry(date, title, content, mood_score, stress_level, 
                         sleep_quality, exercise, meditation, 
                         social_interaction, outdoor_time):
    """
    Process a journal entry to extract sentiment and key metrics.
    All processing happens client-side for privacy.
    
    Args:
        date: Entry date
        title: Entry title
        content: Journal text
        mood_score: User-rated mood (1-10)
        stress_level: User-rated stress (1-10)
        sleep_quality: User-rated sleep quality (1-10)
        exercise: Boolean indicating if user exercised
        meditation: Boolean indicating if user meditated
        social_interaction: Boolean indicating if user had social interaction
        outdoor_time: Boolean indicating if user spent time outdoors
        
    Returns:
        Dictionary with processed entry data
    """
    # Perform sentiment analysis
    sentiment = sia.polarity_scores(content)
    
    # Extract keywords (simplified version - in a real app would be more sophisticated)
    words = content.lower().split()
    
    # Detect emotion indicators
    emotion_keywords = {
        'happy': ['happy', 'joy', 'excited', 'glad', 'wonderful', 'great'],
        'sad': ['sad', 'unhappy', 'depressed', 'down', 'miserable', 'upset'],
        'anxious': ['anxious', 'nervous', 'worried', 'stress', 'fear', 'panic'],
        'angry': ['angry', 'mad', 'frustrated', 'annoyed', 'irritated'],
        'tired': ['tired', 'exhausted', 'fatigue', 'sleepy', 'drained'],
        'calm': ['calm', 'peaceful', 'relaxed', 'tranquil', 'serene']
    }
    
    detected_emotions = {}
    for emotion, keywords in emotion_keywords.items():
        count = sum(1 for word in words if any(keyword in word for keyword in keywords))
        if count > 0:
            detected_emotions[emotion] = count
    
    # Create processed entry
    processed_entry = {
        'date': date,
        'title': title,
        'content': content,
        'mood_score': mood_score,
        'stress_level': stress_level,
        'sleep_quality': sleep_quality,
        'activities': {
            'exercise': exercise,
            'meditation': meditation,
            'social_interaction': social_interaction,
            'outdoor_time': outdoor_time
        },
        'sentiment': {
            'compound': sentiment['compound'],
            'positive': sentiment['pos'],
            'neutral': sentiment['neu'],
            'negative': sentiment['neg']
        },
        'detected_emotions': detected_emotions,
        'word_count': len(words)
    }
    
    return processed_entry

def process_wearable_data(data):
    """
    Process raw wearable data to extract meaningful metrics.
    
    Args:
        data: Raw wearable data dictionary
        
    Returns:
        Dictionary with processed metrics
    """
    # Start with basic metrics that were in the original implementation
    processed_data = {
        'date': data.get('date', datetime.datetime.now().strftime("%Y-%m-%d")),
        'avg_heart_rate': data.get('avg_heart_rate', 0),
        'resting_heart_rate': data.get('resting_heart_rate', 0),
        'heart_rate_variability': data.get('heart_rate_variability', 0),
        'sleep_hours': data.get('sleep_hours', 0),
        'deep_sleep_percentage': data.get('deep_sleep_percentage', 0),
        'rem_sleep_percentage': data.get('rem_sleep_percentage', 0),
        'sleep_disruptions': data.get('sleep_disruptions', 0),
        'steps': data.get('steps', 0),
        'active_calories': data.get('active_calories', 0),
        'activity_minutes': data.get('activity_minutes', 0)
    }
    
    # Add new metrics from enhanced wearable data
    additional_metrics = [
        'blood_oxygen', 'respiratory_rate', 'ecg_normal', 'stress_score',
        'body_battery', 'vo2_max', 'training_status', 'sleep_quality_score',
        'body_temp', 'recovery_score', 'strain_score', 'systolic', 'diastolic',
        'body_fat_percentage', 'muscle_mass', 'mindful_minutes', 'floors_climbed',
        'distance_km', 'active_zone_minutes'
    ]
    
    # Add each metric if it exists in the data
    for metric in additional_metrics:
        if metric in data:
            processed_data[metric] = data[metric]
    
    # Calculate additional metrics
    if processed_data['sleep_hours'] > 0:
        # Sleep efficiency (higher is better)
        deep_sleep_hours = processed_data['sleep_hours'] * (processed_data['deep_sleep_percentage'] / 100)
        rem_sleep_hours = processed_data['sleep_hours'] * (processed_data['rem_sleep_percentage'] / 100)
        processed_data['sleep_efficiency'] = ((deep_sleep_hours + rem_sleep_hours) / processed_data['sleep_hours']) * 100
    else:
        processed_data['sleep_efficiency'] = 0
    
    # Heart rate ranges
    if processed_data['avg_heart_rate'] > 0:
        processed_data['heart_rate_range'] = categorize_heart_rate(processed_data['avg_heart_rate'])
    
    # Calculate overall wellness score based on available metrics
    wellness_score = calculate_wellness_score(processed_data)
    if wellness_score > 0:
        processed_data['wellness_score'] = wellness_score
    
    return processed_data

def calculate_wellness_score(data):
    """
    Calculate an overall wellness score based on available metrics.
    
    Args:
        data: Dictionary with processed wearable data
        
    Returns:
        Integer wellness score from 1-100
    """
    score_components = []
    component_weights = {
        'sleep': 0.3,
        'activity': 0.2,
        'heart': 0.3,
        'stress': 0.2
    }
    
    # Sleep component (sleep efficiency, duration)
    sleep_score = 0
    if data.get('sleep_efficiency', 0) > 0:
        # Sleep efficiency component (0-100)
        sleep_score += min(100, data['sleep_efficiency']) * 0.7
        
        # Sleep duration component (0-100)
        optimal_sleep = 8.0  # Optimal sleep hours
        sleep_duration_score = 100 - (abs(data.get('sleep_hours', 0) - optimal_sleep) / optimal_sleep * 100)
        sleep_score += max(0, sleep_duration_score) * 0.3
        
        score_components.append(('sleep', sleep_score))
    
    # Activity component
    activity_score = 0
    if data.get('steps', 0) > 0:
        # Steps component (10,000 steps = 100)
        steps_score = min(100, (data['steps'] / 10000) * 100)
        activity_score += steps_score * 0.6
        
        # Activity minutes component (30 minutes = 100)
        activity_minutes_score = min(100, (data.get('activity_minutes', 0) / 30) * 100)
        activity_score += activity_minutes_score * 0.4
        
        score_components.append(('activity', activity_score))
    
    # Heart health component
    heart_score = 0
    heart_metrics_count = 0
    
    # Resting heart rate component (optimal range = 60-70)
    if data.get('resting_heart_rate', 0) > 0:
        rhr = data['resting_heart_rate']
        if rhr < 50:
            rhr_score = 80  # Very athletic but might be too low
        elif rhr < 60:
            rhr_score = 90  # Athletic
        elif rhr <= 70:
            rhr_score = 100  # Ideal
        elif rhr <= 80:
            rhr_score = 80  # Normal
        elif rhr <= 90:
            rhr_score = 60  # Elevated
        else:
            rhr_score = 40  # High
            
        heart_score += rhr_score
        heart_metrics_count += 1
    
    # HRV component (higher is better)
    if data.get('heart_rate_variability', 0) > 0:
        hrv = data['heart_rate_variability']
        hrv_score = min(100, max(0, (hrv / 100) * 100))
        heart_score += hrv_score
        heart_metrics_count += 1
        
    # VO2 Max component
    if data.get('vo2_max', 0) > 0:
        vo2 = data['vo2_max']
        # VO2 Max scoring depends on age/gender, but simplified here
        vo2_score = min(100, max(0, (vo2 / 60) * 100))
        heart_score += vo2_score
        heart_metrics_count += 1
        
    # Blood oxygen component
    if data.get('blood_oxygen', 0) > 0:
        spo2 = data['blood_oxygen']
        if spo2 >= 95:
            spo2_score = 100
        elif spo2 >= 90:
            spo2_score = 80
        else:
            spo2_score = 50
        heart_score += spo2_score
        heart_metrics_count += 1
    
    # Compute average heart score if we have metrics
    if heart_metrics_count > 0:
        heart_score = heart_score / heart_metrics_count
        score_components.append(('heart', heart_score))
    
    # Stress component
    if data.get('stress_score', 0) > 0:
        # Lower stress is better, so invert the score
        stress_score = 100 - data['stress_score']
        score_components.append(('stress', stress_score))
    elif data.get('body_battery', 0) > 0:
        # Body battery is a proxy for stress/recovery
        stress_score = data['body_battery']
        score_components.append(('stress', stress_score))
    elif data.get('recovery_score', 0) > 0:
        # Recovery score from devices like Whoop
        stress_score = data['recovery_score']
        score_components.append(('stress', stress_score))
    
    # Calculate weighted average if we have any components
    if score_components:
        total_weight = 0
        weighted_sum = 0
        
        for component, score in score_components:
            weight = component_weights[component]
            weighted_sum += score * weight
            total_weight += weight
            
        if total_weight > 0:
            return round(weighted_sum / total_weight)
    
    return 0

def categorize_heart_rate(avg_heart_rate):
    """Categorize heart rate into meaningful ranges"""
    if avg_heart_rate < 60:
        return "Low"
    elif avg_heart_rate < 70:
        return "Low-Normal"
    elif avg_heart_rate < 80:
        return "Normal"
    elif avg_heart_rate < 90:
        return "High-Normal"
    else:
        return "High"
