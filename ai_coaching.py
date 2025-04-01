"""
AI Coaching module for NeuroSync - Provides advanced mental health coaching 
using fine-tuned GPT models with specialized mental health expertise.
"""

import os
import json
import datetime
from typing import Dict, List, Optional, Union, Any

from modules.openai_integration import openai

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user

# Coaching personas that specialize in different mental health areas
COACHING_PERSONAS = {
    "general": {
        "name": "General Mental Health Coach",
        "description": "A well-rounded mental health coach with expertise in overall wellbeing, stress management, and resilience.",
        "system_prompt": """You are a compassionate mental health coach with expertise in overall wellbeing, stress management, and resilience. 
Your approach is empathetic, evidence-based, and focused on practical strategies that can be implemented in daily life.
Analyze the user's data thoroughly and provide personalized guidance that addresses their specific needs and circumstances.
Format your responses with clear sections, concise language, and actionable steps."""
    },
    "anxiety": {
        "name": "Anxiety Specialist",
        "description": "Specializes in anxiety management, panic disorders, and techniques to reduce anxious thoughts.",
        "system_prompt": """You are a specialized anxiety coach with deep expertise in anxiety management, panic disorders, and cognitive-behavioral techniques.
Your approach is gentle, reassuring, and grounded in evidence-based practices for anxiety reduction.
Analyze the user's data for signs of anxiety patterns and provide personalized techniques that can help reduce anxious thoughts and physical symptoms.
Focus on breathing techniques, cognitive restructuring, mindfulness for anxiety, and gradual exposure strategies when appropriate.
Format your responses with clear, simple steps that can be implemented during moments of anxiety."""
    },
    "depression": {
        "name": "Depression and Mood Support Coach",
        "description": "Focuses on mood improvement, combating negative thought patterns, and behavioral activation.",
        "system_prompt": """You are a specialized depression and mood support coach with expertise in evidence-based approaches for improving mood and combating negative thought patterns.
Your approach is warm, encouraging, and focused on gradual, sustainable improvement.
Analyze the user's data for signs of low mood patterns and provide personalized strategies focusing on behavioral activation, challenging negative thoughts, and building positive experiences.
Emphasize small, achievable steps and celebrate progress, while being sensitive to the challenges of motivation that often accompany depression.
Format your responses with gentle encouragement and clear, manageable action items."""
    },
    "sleep": {
        "name": "Sleep Improvement Specialist",
        "description": "Expert in sleep hygiene, insomnia management, and techniques to improve sleep quality.",
        "system_prompt": """You are a specialized sleep coach with expertise in sleep hygiene, insomnia management, and circadian rhythm optimization.
Your approach is methodical, science-based, and focused on sustainable sleep improvements.
Analyze the user's sleep data and patterns thoroughly and provide personalized recommendations for improving sleep quality and duration.
Focus on sleep hygiene practices, bedtime routines, environment optimization, and cognitive techniques for sleep-related anxieties.
Format your responses with a clear distinction between immediate actions and longer-term habits to develop."""
    },
    "mindfulness": {
        "name": "Mindfulness and Meditation Guide",
        "description": "Specializes in mindfulness practices, meditation techniques, and present-moment awareness.",
        "system_prompt": """You are a specialized mindfulness and meditation coach with expertise in various meditation techniques, present-moment awareness practices, and mindful living.
Your approach is calm, centered, and accessible to practitioners of all experience levels.
Provide personalized mindfulness practices that match the user's experience level, available time, and specific mental health needs.
Offer clear instruction in meditation techniques, informal mindfulness practices for daily life, and ways to integrate mindfulness into challenging situations.
Format your responses with graded practice suggestions from beginner to more advanced, and include both quick exercises and deeper practices."""
    },
    "stress": {
        "name": "Stress Management Expert",
        "description": "Focuses on stress reduction techniques, burnout prevention, and work-life balance strategies.",
        "system_prompt": """You are a specialized stress management coach with expertise in stress reduction techniques, burnout prevention, and creating sustainable work-life balance.
Your approach is practical, preventative, and tailored to modern life challenges.
Analyze the user's stress patterns, triggers, and current coping mechanisms to provide personalized stress management strategies.
Focus on physiological stress reduction, boundary setting, time management, cognitive reframing of stressors, and recovery practices.
Format your responses with a mix of immediate stress relief techniques and longer-term stress resilience strategies."""
    }
}

def get_available_coaching_personas() -> List[Dict[str, str]]:
    """
    Returns the list of available coaching personas with their names and descriptions.
    
    Returns:
        List of dictionaries with persona information
    """
    personas = []
    for persona_id, persona in COACHING_PERSONAS.items():
        personas.append({
            "id": persona_id,
            "name": persona["name"],
            "description": persona["description"]
        })
    return personas

def generate_coaching_advice(
    user_data: Dict[str, Any],
    coaching_focus: str,
    persona_id: str = "general",
    session_history: Optional[List[Dict[str, str]]] = None,
    model: str = "gpt-4o"
) -> str:
    """
    Generate personalized coaching advice using specialized mental health personas.
    
    Args:
        user_data: Dictionary containing user's journal and wearable data
        coaching_focus: Specific area or question the user wants coaching on
        persona_id: ID of the coaching persona to use (from COACHING_PERSONAS)
        session_history: Optional list of previous interactions in this coaching session
        model: OpenAI model to use
        
    Returns:
        Coaching advice text
    """
    # Select the appropriate persona, defaulting to general if not found
    persona = COACHING_PERSONAS.get(persona_id, COACHING_PERSONAS["general"])
    
    # Create the system prompt
    system_prompt = persona["system_prompt"]
    
    # Initialize messages with system prompt
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add session history if provided
    if session_history:
        messages.extend(session_history)
    
    # Create a detailed user prompt based on data and coaching focus
    user_prompt = _create_coaching_prompt(user_data, coaching_focus)
    
    # Add the user prompt to messages
    messages.append({"role": "user", "content": user_prompt})
    
    try:
        # Generate response from OpenAI
        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1200,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        # Return a graceful error message
        print(f"Error generating coaching advice: {e}")
        return f"""
# Coaching Advice Unavailable

I apologize, but I'm unable to generate personalized coaching at the moment due to a technical issue.

**Error:** {str(e)}

Please try again later or select a different coaching focus or persona.
        """

def analyze_progress(
    journal_entries: List[Dict[str, Any]],
    wearable_data: List[Dict[str, Any]],
    coaching_history: List[Dict[str, Any]],
    timeframe_days: int = 30,
    model: str = "gpt-4o"
) -> Dict[str, Any]:
    """
    Analyze user's progress over time based on journal entries, wearable data,
    and coaching interactions.
    
    Args:
        journal_entries: List of journal entry dictionaries
        wearable_data: List of wearable data dictionaries
        coaching_history: List of previous coaching interactions
        timeframe_days: Number of days to analyze
        model: OpenAI model to use
        
    Returns:
        Dictionary with progress analysis results
    """
    cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=timeframe_days)).strftime("%Y-%m-%d")
    
    # Filter data to the specified timeframe
    recent_journals = [j for j in journal_entries if j.get('date', '') >= cutoff_date]
    recent_wearables = [w for w in wearable_data if w.get('date', '') >= cutoff_date]
    recent_coaching = [c for c in coaching_history if c.get('date', '') >= cutoff_date]
    
    if not recent_journals or len(recent_journals) < 2:
        return {
            "sufficient_data": False,
            "message": "Insufficient journal data to analyze progress. Please continue journaling regularly."
        }
    
    # Extract relevant metrics for trend analysis
    mood_trend = [{'date': j.get('date', ''), 'score': j.get('mood_score', 0)} for j in recent_journals]
    stress_trend = [{'date': j.get('date', ''), 'score': j.get('stress_level', 0)} for j in recent_journals]
    
    # Include wearable data if available
    sleep_trend = []
    activity_trend = []
    if recent_wearables:
        sleep_trend = [{'date': w.get('date', ''), 'hours': w.get('sleep_hours', 0)} for w in recent_wearables]
        activity_trend = [{'date': w.get('date', ''), 'steps': w.get('steps', 0)} for w in recent_wearables]
    
    # Create prompt for analysis
    analysis_prompt = f"""
I need an analysis of a user's mental health progress over the past {timeframe_days} days.

MOOD DATA:
{json.dumps(mood_trend)}

STRESS DATA:
{json.dumps(stress_trend)}

SLEEP DATA:
{json.dumps(sleep_trend)}

ACTIVITY DATA:
{json.dumps(activity_trend)}

COACHING FOCUS AREAS:
{", ".join(set([c.get('focus', 'general') for c in recent_coaching]))}

Please provide a comprehensive analysis of:
1. Overall trend in mood and mental wellbeing
2. Progress in areas the user has been focusing on
3. Correlations between different metrics (e.g., sleep and mood)
4. Areas of improvement and areas that need continued attention
5. Recommendations for next steps in their mental health journey

Format your response as a JSON object with the following keys:
- overall_trend: A summary of the general direction of the user's mental health
- key_improvements: List of areas where the user has shown progress
- challenge_areas: List of areas that need continued attention
- correlations: Any notable relationships between different metrics
- recommendations: Specific, actionable suggestions for continued progress
- wellness_score: A score from 1-100 representing overall mental wellness trend
"""
    
    try:
        # Generate analysis from OpenAI
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a mental health analytics expert specializing in progress assessment and trend analysis."},
                {"role": "user", "content": analysis_prompt}
            ],
            response_format={"type": "json_object"},
        )
        
        # Parse the response
        result = json.loads(response.choices[0].message.content)
        result["sufficient_data"] = True
        return result
        
    except Exception as e:
        print(f"Error analyzing progress: {e}")
        return {
            "sufficient_data": True,
            "overall_trend": "Unable to analyze due to technical error",
            "key_improvements": ["Data available but analysis failed"],
            "challenge_areas": ["System error in analysis"],
            "correlations": [],
            "recommendations": ["Try again later", "Continue with regular journaling and tracking"],
            "wellness_score": 50,
            "error": str(e)
        }

def generate_personalized_exercise(
    user_data: Dict[str, Any],
    exercise_type: str,
    duration_minutes: int = 5,
    difficulty: str = "beginner",
    model: str = "gpt-4o"
) -> Dict[str, str]:
    """
    Generate a personalized mental health exercise tailored to the user's needs.
    
    Args:
        user_data: Dictionary containing user's journal and wearable data
        exercise_type: Type of exercise (meditation, breathing, cognitive, etc.)
        duration_minutes: Desired duration of the exercise
        difficulty: Difficulty level (beginner, intermediate, advanced)
        model: OpenAI model to use
        
    Returns:
        Dictionary with exercise details
    """
    # Create the exercise prompt
    exercise_prompt = f"""
Create a personalized {exercise_type} exercise for a user with the following profile:

RECENT MOOD: {user_data.get('mood_score', 'Unknown')}/10
STRESS LEVEL: {user_data.get('stress_level', 'Unknown')}/10
SLEEP QUALITY: {user_data.get('sleep_quality', 'Unknown')}/10
PRIMARY CONCERNS: {', '.join(user_data.get('key_concerns', ['General wellbeing']))}

The exercise should:
- Take approximately {duration_minutes} minutes to complete
- Be appropriate for a {difficulty} level practitioner
- Address the user's specific mental health needs
- Include clear, step-by-step instructions
- Provide guidance on how to integrate this practice into daily life

Format your response as a JSON object with the following keys:
- title: A brief, engaging title for the exercise
- introduction: A short paragraph explaining the purpose and benefits
- materials_needed: Any items or preparation required (if none, specify "None needed")
- steps: Numbered list of instructions
- tips: Additional guidance for effective practice
- variations: 1-2 alternative ways to perform the exercise for different situations
- daily_integration: How to incorporate this into a regular routine
"""
    
    try:
        # Generate exercise from OpenAI
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert in mental health exercises and interventions, specializing in creating personalized practices for individuals."},
                {"role": "user", "content": exercise_prompt}
            ],
            response_format={"type": "json_object"},
        )
        
        # Parse the response
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        print(f"Error generating exercise: {e}")
        return {
            "title": "Basic Mindful Breathing Exercise",
            "introduction": "This simple breathing exercise can help center your mind and reduce stress.",
            "materials_needed": "None needed",
            "steps": [
                "Find a comfortable seated position",
                "Close your eyes or maintain a soft gaze",
                "Breathe naturally and observe your breath",
                "Count each inhale and exhale up to 10, then start again",
                "Continue for 5 minutes"
            ],
            "tips": "If your mind wanders, gently return focus to your breath without judgment",
            "variations": "Can be done standing or lying down if preferred",
            "daily_integration": "Practice first thing in the morning or during a stressful moment",
            "error": str(e)
        }

def _create_coaching_prompt(user_data: Dict[str, Any], coaching_focus: str) -> str:
    """
    Create a detailed prompt for AI coaching based on user data and focus area.
    
    Args:
        user_data: Dictionary containing user's journal and wearable data
        coaching_focus: Specific area or question the user wants coaching on
        
    Returns:
        Formatted prompt string
    """
    journal_data = user_data.get('journal_data', {})
    wearable_data = user_data.get('wearable_data', {})
    
    prompt = f"""
I'm seeking personalized mental health coaching about: {coaching_focus}

MY CURRENT STATE:
- Mood: {journal_data.get('mood_score', 'N/A')}/10
- Stress: {journal_data.get('stress_level', 'N/A')}/10
- Sleep: {journal_data.get('sleep_quality', 'N/A')}/10
- Recent activities: {_format_activities(journal_data)}
- Recent journal entry: "{journal_data.get('content', 'No recent journal entry')}"

"""
    
    # Add wearable data if available
    if wearable_data:
        prompt += f"""
MY HEALTH METRICS:
- Heart rate: {wearable_data.get('avg_heart_rate', 'N/A')} bpm
- Sleep duration: {wearable_data.get('sleep_hours', 'N/A')} hours
- Physical activity: {wearable_data.get('steps', 'N/A')} steps
- Activity minutes: {wearable_data.get('activity_minutes', 'N/A')} minutes
"""

    if 'wellness_score' in wearable_data:
        prompt += f"- Overall wellness score: {wearable_data.get('wellness_score', 'N/A')}/100\n"
    
    # Add specific coaching requests
    prompt += f"""
COACHING REQUEST:
I would like specific guidance on {coaching_focus}. Please provide:
1. An assessment of my current state related to this area
2. Practical strategies I can implement immediately
3. Longer-term approaches for sustainable improvement
4. How I can measure my progress in this area
"""
    
    return prompt

def _format_activities(journal_data: Dict[str, Any]) -> str:
    """Format journal activities into a readable string"""
    activities = []
    
    if journal_data.get('exercise', False):
        activities.append("exercise")
    if journal_data.get('meditation', False):
        activities.append("meditation")
    if journal_data.get('social_interaction', False):
        activities.append("social interaction")
    if journal_data.get('outdoor_time', False):
        activities.append("time outdoors")
    
    if activities:
        return ", ".join(activities)
    else:
        return "none specified"