import os
import json
from modules.openai_integration import (
    analyze_journal_sentiment as openai_analyze_journal_sentiment,
    generate_coping_strategies as openai_generate_coping_strategies,
    analyze_sleep_patterns as openai_analyze_sleep_patterns,
    generate_fallback_strategies as openai_generate_fallback_strategies
)

# Get API key from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

def generate_coping_strategies(journal_data, wearable_data, focus_areas, time_available, environment):
    """
    Generate personalized coping strategies using OpenAI based on user data.
    
    Args:
        journal_data: Dictionary with recent journal entry data
        wearable_data: Dictionary with recent wearable data
        focus_areas: List of focus areas selected by the user
        time_available: Number of minutes available for activities
        environment: String indicating where strategies will be implemented
        
    Returns:
        String with personalized coping strategies
    """
    try:
        # If no API key is available, return generic strategies
        if not OPENAI_API_KEY:
            return openai_generate_fallback_strategies(focus_areas, time_available, environment)
        
        # Call the OpenAI integration module to generate strategies
        return openai_generate_coping_strategies(journal_data, wearable_data, focus_areas, time_available, environment)
        
    except Exception as e:
        print(f"Error generating strategies: {e}")
        return openai_generate_fallback_strategies(focus_areas, time_available, environment)

def analyze_journal_sentiment(journal_text):
    """
    Analyze the sentiment and emotional content of a journal entry.
    
    Args:
        journal_text: String containing the journal entry
        
    Returns:
        Dictionary with sentiment analysis results
    """
    try:
        if not OPENAI_API_KEY:
            return {
                "sentiment": "neutral",
                "primary_emotions": ["unknown"],
                "sentiment_score": 0.0
            }
        
        # Call the OpenAI integration module to analyze sentiment
        return openai_analyze_journal_sentiment(journal_text)
        
    except Exception as e:
        print(f"Error analyzing journal sentiment: {e}")
        return {
            "sentiment": "neutral",
            "primary_emotions": ["unknown"],
            "sentiment_score": 0.0
        }

def analyze_sleep_patterns(sleep_data, journal_data):
    """
    Analyze sleep patterns and their relationship to mood and stress.
    
    Args:
        sleep_data: List of dictionaries with sleep metrics
        journal_data: List of dictionaries with journal entries
        
    Returns:
        Dictionary with sleep analysis insights
    """
    try:
        if not OPENAI_API_KEY:
            return {
                "overall_assessment": "Unable to analyze due to API key not available",
                "sleep_mood_correlation": "Data unavailable",
                "key_issues": ["API key not configured"],
                "recommendations": ["Please configure OpenAI API key"],
                "positive_habits": ["Continuing to track sleep data"]
            }
        
        # Call the OpenAI integration module to analyze sleep patterns
        return openai_analyze_sleep_patterns(sleep_data, journal_data)
        
    except Exception as e:
        print(f"Error analyzing sleep patterns: {e}")
        return {
            "overall_assessment": "Unable to analyze due to an error",
            "sleep_mood_correlation": "Error in analysis",
            "key_issues": ["Analysis error"],
            "recommendations": ["Try again later"],
            "positive_habits": ["Continuing to track sleep data"],
            "error": str(e)
        }
