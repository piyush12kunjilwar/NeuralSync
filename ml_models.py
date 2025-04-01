import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import datetime

def analyze_mood_patterns(journal_entries, wearable_data):
    """
    Analyze patterns between mood/journal entries and wearable data.
    
    Args:
        journal_entries: List of processed journal entries
        wearable_data: List of processed wearable data
        
    Returns:
        List of insights as strings
    """
    # Initialize insights list
    insights = []
    
    # Check if we have enough data
    if len(journal_entries) < 3 or len(wearable_data) < 3:
        insights.append("Not enough data to generate reliable insights yet. Keep logging entries and syncing your wearable device.")
        return insights
    
    # Match journal entries with corresponding wearable data
    matched_data = []
    
    for entry in journal_entries:
        entry_date = entry.get('date')
        if entry_date:
            # Find matching wearable data for this date
            matching_wearable = next(
                (w for w in wearable_data if w.get('date') == entry_date), 
                None
            )
            
            if matching_wearable:
                matched_data.append({
                    'date': entry_date,
                    'mood_score': entry.get('mood_score', 0),
                    'stress_level': entry.get('stress_level', 0),
                    'sleep_quality': entry.get('sleep_quality', 0),
                    'sentiment_compound': entry.get('sentiment', {}).get('compound', 0),
                    'activities': entry.get('activities', {}),
                    'sleep_hours': matching_wearable.get('sleep_hours', 0),
                    'deep_sleep_percentage': matching_wearable.get('deep_sleep_percentage', 0),
                    'avg_heart_rate': matching_wearable.get('avg_heart_rate', 0),
                    'steps': matching_wearable.get('steps', 0),
                    'activity_minutes': matching_wearable.get('activity_minutes', 0)
                })
    
    # If we have enough matched data, analyze patterns
    if len(matched_data) >= 3:
        # Analyze sleep and mood correlation
        sleep_mood_corr = calculate_correlation(
            [d['sleep_hours'] for d in matched_data],
            [d['mood_score'] for d in matched_data]
        )
        
        if abs(sleep_mood_corr) > 0.4:
            if sleep_mood_corr > 0:
                insights.append("📊 Analysis shows that your mood tends to be better on days when you get more sleep.")
            else:
                insights.append("📊 Interestingly, there seems to be a negative correlation between sleep hours and mood in your data.")
        
        # Analyze steps/activity and mood
        activity_mood_corr = calculate_correlation(
            [d['steps'] for d in matched_data],
            [d['mood_score'] for d in matched_data]
        )
        
        if abs(activity_mood_corr) > 0.4:
            if activity_mood_corr > 0:
                insights.append("📊 You tend to report better moods on days with more physical activity.")
            else:
                insights.append("📊 Your data suggests physical activity might not be improving your mood as expected.")
        
        # Analyze heart rate and stress
        hr_stress_corr = calculate_correlation(
            [d['avg_heart_rate'] for d in matched_data],
            [d['stress_level'] for d in matched_data]
        )
        
        if abs(hr_stress_corr) > 0.3:
            if hr_stress_corr > 0:
                insights.append("📊 Your average heart rate tends to be higher on days when you report more stress.")
            else:
                insights.append("📊 Despite reporting stress, your heart rate doesn't show typical elevation patterns.")
        
        # Check for activity patterns
        exercise_days = [d for d in matched_data if d['activities'].get('exercise', False)]
        non_exercise_days = [d for d in matched_data if not d['activities'].get('exercise', False)]
        
        if exercise_days and non_exercise_days:
            avg_mood_with_exercise = sum(d['mood_score'] for d in exercise_days) / len(exercise_days)
            avg_mood_without_exercise = sum(d['mood_score'] for d in non_exercise_days) / len(non_exercise_days)
            
            if avg_mood_with_exercise > avg_mood_without_exercise + 1:
                insights.append("📊 On days when you exercise, your mood score is significantly higher (about " + 
                               f"{round(avg_mood_with_exercise - avg_mood_without_exercise, 1)} points).")
        
        # Check meditation impact
        meditation_days = [d for d in matched_data if d['activities'].get('meditation', False)]
        non_meditation_days = [d for d in matched_data if not d['activities'].get('meditation', False)]
        
        if meditation_days and non_meditation_days:
            avg_stress_with_meditation = sum(d['stress_level'] for d in meditation_days) / len(meditation_days)
            avg_stress_without_meditation = sum(d['stress_level'] for d in non_meditation_days) / len(non_meditation_days)
            
            if avg_stress_without_meditation > avg_stress_with_meditation + 1:
                insights.append("📊 Meditation appears to be effective for you - your stress levels are lower on days when you meditate.")
    
    # Add general insights if we don't have enough specific ones
    if len(insights) < 2:
        insights.append("Continue tracking your mood and activities to receive more personalized insights.")
        insights.append("Consider maintaining consistent sleep and exercise routines, as these typically have positive effects on mental health.")
    
    return insights

def predict_stress_level(latest_journal, latest_wearable):
    """
    Predict current stress level based on latest data.
    
    Args:
        latest_journal: Most recent journal entry
        latest_wearable: Most recent wearable data
        
    Returns:
        Dictionary with predicted stress level and contributing factors
    """
    # Base prediction on a combination of factors
    # In a real app, this would use a properly trained ML model
    
    base_stress = 5  # Default mid-level stress
    contributing_factors = {}
    recommendations = []
    
    # Factor 1: Recent sleep quality
    if latest_wearable and 'sleep_hours' in latest_wearable:
        sleep_hours = latest_wearable['sleep_hours']
        sleep_factor = 0
        
        if sleep_hours < 6:
            sleep_factor = 1.5  # Increases stress
            contributing_factors["Low sleep (less than 6 hours)"] = "High impact"
            recommendations.append("Prioritize improving your sleep duration. Aim for 7-8 hours.")
        elif sleep_hours > 8:
            sleep_factor = -1  # Decreases stress
            contributing_factors["Good sleep duration"] = "Positive factor"
        else:
            sleep_factor = -0.5  # Slightly decreases stress
            contributing_factors["Adequate sleep"] = "Slight positive"
        
        base_stress += sleep_factor
    
    # Factor 2: Heart rate compared to personal baseline
    if latest_wearable and 'avg_heart_rate' in latest_wearable:
        heart_rate = latest_wearable['avg_heart_rate']
        hr_factor = 0
        
        if heart_rate > 80:
            hr_factor = 1  # Increases stress
            contributing_factors["Elevated heart rate"] = "Moderate impact"
            recommendations.append("Try deep breathing exercises to help lower your heart rate.")
        elif heart_rate < 65:
            hr_factor = -0.5  # Slightly decreases stress
            contributing_factors["Low resting heart rate"] = "Positive factor"
        
        base_stress += hr_factor
    
    # Factor 3: Recent physical activity
    if latest_wearable and 'steps' in latest_wearable:
        steps = latest_wearable['steps']
        activity_factor = 0
        
        if steps < 3000:
            activity_factor = 0.5  # Slightly increases stress
            contributing_factors["Low physical activity"] = "Slight negative"
            recommendations.append("Try to incorporate more walking into your day. Even short walks can help reduce stress.")
        elif steps > 8000:
            activity_factor = -1  # Decreases stress
            contributing_factors["Good physical activity"] = "Positive factor"
        
        base_stress += activity_factor
    
    # Factor 4: Journal sentiment
    if latest_journal and 'sentiment' in latest_journal:
        sentiment = latest_journal['sentiment'].get('compound', 0)
        sentiment_factor = 0
        
        if sentiment < -0.3:
            sentiment_factor = 1.5  # Significantly increases stress
            contributing_factors["Negative journal sentiment"] = "High impact"
            recommendations.append("Your journal entries show negative patterns. Consider mindfulness practices to help shift perspective.")
        elif sentiment > 0.3:
            sentiment_factor = -1  # Decreases stress
            contributing_factors["Positive outlook"] = "Positive factor"
        
        base_stress += sentiment_factor
    
    # Factor 5: Recent activities
    if latest_journal and 'activities' in latest_journal:
        activities = latest_journal['activities']
        
        if activities.get('exercise', False):
            base_stress -= 0.5
            contributing_factors["Recent exercise"] = "Positive factor"
        
        if activities.get('meditation', False):
            base_stress -= 1
            contributing_factors["Meditation practice"] = "Significant positive"
        
        if activities.get('outdoor_time', False):
            base_stress -= 0.5
            contributing_factors["Time outdoors"] = "Positive factor"
        
        if not activities.get('social_interaction', False):
            base_stress += 0.5
            contributing_factors["Limited social interaction"] = "Slight negative"
            recommendations.append("Consider connecting with friends or family, even briefly.")
    
    # Ensure stress level is between 1-10
    predicted_stress = max(1, min(10, round(base_stress)))
    
    # Add general recommendations if we don't have enough specific ones
    if len(recommendations) < 2:
        recommendations.append("Practice regular deep breathing throughout the day.")
        recommendations.append("Take short breaks from screens and work to reset your mind.")
    
    return {
        'predicted_stress_level': predicted_stress,
        'contributing_factors': contributing_factors,
        'recommendations': recommendations
    }

def calculate_correlation(x, y):
    """Calculate Pearson correlation coefficient between two variables"""
    if len(x) != len(y) or len(x) < 2:
        return 0
    
    x = np.array(x)
    y = np.array(y)
    
    # Remove any nan values
    mask = ~(np.isnan(x) | np.isnan(y))
    x = x[mask]
    y = y[mask]
    
    if len(x) < 2:
        return 0
    
    # Calculate correlation
    try:
        correlation = np.corrcoef(x, y)[0, 1]
        return correlation
    except:
        return 0
