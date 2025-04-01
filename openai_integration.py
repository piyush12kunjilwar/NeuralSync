import json
import os
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def analyze_journal_sentiment(journal_text):
    """
    Analyze the sentiment and emotional content of a journal entry.
    
    Args:
        journal_text: String containing the journal entry
        
    Returns:
        Dictionary with sentiment analysis results
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a mental health sentiment analysis expert. "
                    + "Analyze the sentiment of the journal entry and provide an emotional assessment. "
                    + "Respond with JSON in this format: "
                    + "{'sentiment_score': number from 1-10, 'primary_emotion': string, "
                    + "'emotional_tone': string, 'key_concerns': [strings], 'strengths': [strings]}"
                },
                {"role": "user", "content": journal_text},
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "sentiment_score": 5,
            "primary_emotion": "neutral",
            "emotional_tone": "moderate",
            "key_concerns": ["Unable to analyze due to API error"],
            "strengths": ["Journaling practice"],
            "error": str(e)
        }

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
        prompt = create_strategy_prompt(journal_data, wearable_data, focus_areas, time_available, environment)
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a compassionate mental health expert specializing in personalized coping strategies. "
                    + "Based on the data provided, suggest practical, evidence-based coping strategies. "
                    + "Be warm, supportive, and focus on achievable actions. "
                    + "Format your response with markdown headers, bullet points, and concise explanations."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return generate_fallback_strategies(focus_areas, time_available, environment)

def create_strategy_prompt(journal_data, wearable_data, focus_areas, time_available, environment):
    """Create a detailed prompt for the OpenAI API based on user data"""
    prompt = f"""I need personalized mental health coping strategies based on the following information:

JOURNAL DATA:
- Most recent mood: {journal_data.get('mood_score', 'N/A')}/10
- Stress level: {journal_data.get('stress_level', 'N/A')}/10
- Sleep quality: {journal_data.get('sleep_quality', 'N/A')}/10
- Exercise today: {'Yes' if journal_data.get('exercise', False) else 'No'}
- Meditation today: {'Yes' if journal_data.get('meditation', False) else 'No'}
- Social interaction: {'Yes' if journal_data.get('social_interaction', False) else 'No'}
- Time outdoors: {'Yes' if journal_data.get('outdoor_time', False) else 'No'}
- Journal entry: "{journal_data.get('content', 'No content available')}"

WEARABLE DATA:
- Average heart rate: {wearable_data.get('avg_heart_rate', 'N/A')} bpm
- Sleep duration: {wearable_data.get('sleep_hours', 'N/A')} hours
- Steps today: {wearable_data.get('steps', 'N/A')}
- Activity minutes: {wearable_data.get('active_minutes', 'N/A')} minutes

PREFERENCES:
- Focus areas: {', '.join(focus_areas)}
- Time available: {time_available} minutes
- Environment: {environment}

Please provide 3-5 specific coping strategies that are:
1. Evidence-based and effective
2. Tailored to the mood, stress, and physical data
3. Appropriate for the specified time frame and environment
4. Focused on the requested areas
5. Clear and actionable
"""
    return prompt

def generate_fallback_strategies(focus_areas, time_available, environment):
    """Generate generic coping strategies when OpenAI API is unavailable"""
    strategies = [
        "### Deep Breathing Exercise\n- Take 5 minutes to practice deep, diaphragmatic breathing\n- Inhale for 4 counts, hold for 2, exhale for 6\n- Focus on the sensation of your breath",
        "### Mindful Observation\n- Choose an object in your environment and observe it closely for 3 minutes\n- Notice its colors, textures, and details\n- This practice helps anchor you to the present moment",
        "### Brief Physical Movement\n- Stand up and stretch your body gently\n- Roll your shoulders, neck, and wrists\n- Even brief movement can help reduce tension and improve mood",
        "### Gratitude Practice\n- Take a moment to identify three things you're grateful for today\n- They can be simple everyday things\n- This helps shift perspective toward positive aspects of life",
        "### Progressive Muscle Relaxation\n- Tense and then release each muscle group in your body\n- Work from toes to head\n- Notice the difference between tension and relaxation"
    ]
    
    # Filter strategies based on available time
    if time_available < 5:
        strategies = [s for s in strategies if "5 minutes" not in s]
    
    # Format response
    response = f"""# Coping Strategies

**Note:** These are general evidence-based strategies that can be helpful for many people. They're designed to be used in a {environment} environment and take {time_available} minutes or less.

"""
    
    # Add strategies based on focus areas
    added_strategies = 0
    for area in focus_areas:
        if area.lower() in ["breathing", "relaxation"] and added_strategies < 3:
            response += f"\n{strategies[0]}\n"
            added_strategies += 1
        elif area.lower() in ["mindfulness", "present"] and added_strategies < 3:
            response += f"\n{strategies[1]}\n"
            added_strategies += 1
        elif area.lower() in ["physical", "movement", "exercise"] and added_strategies < 3:
            response += f"\n{strategies[2]}\n"
            added_strategies += 1
        elif area.lower() in ["gratitude", "positive", "perspective"] and added_strategies < 3:
            response += f"\n{strategies[3]}\n"
            added_strategies += 1
        elif area.lower() in ["muscle", "tension", "relaxation"] and added_strategies < 3:
            response += f"\n{strategies[4]}\n"
            added_strategies += 1
    
    # Ensure at least 2 strategies are included
    if added_strategies < 2:
        for i in range(min(2 - added_strategies, len(strategies))):
            response += f"\n{strategies[i]}\n"
    
    return response

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
        # Prepare data for analysis
        sleep_entries = []
        for entry in sleep_data[-7:]:  # Last 7 entries
            sleep_entries.append({
                "date": entry.get("date", ""),
                "sleep_hours": entry.get("sleep_hours", 0),
                "sleep_quality": entry.get("sleep_quality", 0),
                "deep_sleep_percentage": entry.get("deep_sleep_percentage", 0)
            })
        
        journal_entries = []
        for entry in journal_data[-7:]:  # Last 7 entries
            journal_entries.append({
                "date": entry.get("date", ""),
                "mood_score": entry.get("mood_score", 0),
                "stress_level": entry.get("stress_level", 0),
                "content_summary": entry.get("content", "")[:100] + "..." if len(entry.get("content", "")) > 100 else entry.get("content", "")
            })
        
        # Create the prompt for analysis
        prompt = f"""Analyze the following sleep data and journal entries:

SLEEP DATA:
{json.dumps(sleep_entries, indent=2)}

JOURNAL DATA:
{json.dumps(journal_entries, indent=2)}

Provide a sleep pattern analysis that includes:
1. Overall sleep quality assessment
2. Correlation between sleep and mood/stress
3. Most significant sleep issues
4. Actionable recommendations for improvement
5. Positive sleep habits to maintain

Format as JSON with these keys: 'overall_assessment', 'sleep_mood_correlation', 'key_issues', 'recommendations', 'positive_habits'
"""

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a sleep scientist specializing in the relationship between sleep and mental health. "
                    + "Analyze sleep data and provide evidence-based insights and recommendations."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "overall_assessment": "Unable to analyze due to API error",
            "sleep_mood_correlation": "Data unavailable",
            "key_issues": ["API connection error"],
            "recommendations": ["Try again later", "Focus on consistent sleep schedule"],
            "positive_habits": ["Continuing to track sleep data"],
            "error": str(e)
        }