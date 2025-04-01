"""
Zen Garden Module for NeuroSync - A calming, interactive meditation mini-game
that allows users to create and maintain a virtual zen garden for mindfulness practice.
"""
import datetime
import random
from typing import Dict, List, Any, Optional

def create_default_garden() -> Dict[str, Any]:
    """
    Create a default zen garden configuration for new users.
    
    Returns:
        Dictionary with default garden configuration
    """
    return {
        "sand_pattern": "waves",
        "stones": [
            {"x": 30, "y": 40, "size": 15, "type": "round"},
            {"x": 70, "y": 60, "size": 20, "type": "rough"},
            {"x": 50, "y": 20, "size": 10, "type": "flat"}
        ],
        "plants": [
            {"x": 20, "y": 70, "type": "bonsai", "size": 20},
            {"x": 80, "y": 30, "type": "bamboo", "size": 15}
        ],
        "decorations": [
            {"x": 90, "y": 90, "type": "lantern"},
            {"x": 10, "y": 10, "type": "bridge"}
        ],
        "last_modified": datetime.datetime.now().strftime("%Y-%m-%d"),
        "meditation_sessions": []
    }

def record_meditation_session(garden_data: Dict[str, Any], duration_minutes: int) -> Dict[str, Any]:
    """
    Record a completed meditation session in the garden data.
    
    Args:
        garden_data: Dictionary containing garden configuration
        duration_minutes: Length of meditation session in minutes
        
    Returns:
        Updated garden_data dictionary
    """
    if "meditation_sessions" not in garden_data:
        garden_data["meditation_sessions"] = []
    
    # Add the new session
    new_session = {
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.datetime.now().strftime("%H:%M"),
        "duration_minutes": duration_minutes,
        "notes": ""
    }
    
    garden_data["meditation_sessions"].append(new_session)
    garden_data["last_modified"] = datetime.datetime.now().strftime("%Y-%m-%d")
    
    return garden_data

def get_meditation_stats(garden_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate meditation statistics from garden data.
    
    Args:
        garden_data: Dictionary containing garden configuration and meditation sessions
        
    Returns:
        Dictionary with meditation statistics
    """
    sessions = garden_data.get("meditation_sessions", [])
    
    if not sessions:
        return {
            "total_sessions": 0,
            "total_minutes": 0,
            "longest_session": 0,
            "average_duration": 0,
            "streak_days": 0,
            "last_session": None
        }
    
    # Calculate stats
    total_sessions = len(sessions)
    total_minutes = sum(session.get("duration_minutes", 0) for session in sessions)
    longest_session = max(session.get("duration_minutes", 0) for session in sessions)
    average_duration = round(total_minutes / total_sessions, 1)
    
    # Calculate streak
    sorted_sessions = sorted(sessions, key=lambda x: x.get("date", ""), reverse=True)
    last_session = sorted_sessions[0].get("date", None)
    
    # Count consecutive days
    streak = 1
    if len(sorted_sessions) > 1:
        today = datetime.datetime.now().date()
        latest_date = datetime.datetime.strptime(sorted_sessions[0].get("date", ""), "%Y-%m-%d").date()
        
        # Check if meditation happened today or yesterday
        if (today - latest_date).days > 1:
            streak = 0
        else:
            dates = [datetime.datetime.strptime(s.get("date", ""), "%Y-%m-%d").date() for s in sorted_sessions]
            unique_dates = set()
            
            for date in sorted(dates, reverse=True):
                unique_dates.add(date.strftime("%Y-%m-%d"))
                prev_date = date - datetime.timedelta(days=1)
                if prev_date.strftime("%Y-%m-%d") not in unique_dates:
                    break
                streak += 1
    
    return {
        "total_sessions": total_sessions,
        "total_minutes": total_minutes,
        "longest_session": longest_session,
        "average_duration": average_duration,
        "streak_days": streak,
        "last_session": last_session
    }

def generate_zen_wisdom() -> str:
    """
    Generate a random zen wisdom quote.
    
    Returns:
        String containing a zen wisdom quote
    """
    zen_quotes = [
        "The obstacle is the path.",
        "When you reach the top of the mountain, keep climbing.",
        "Before enlightenment, chop wood, carry water. After enlightenment, chop wood, carry water.",
        "The quieter you become, the more you can hear.",
        "Wherever you are, be there totally.",
        "When thoughts arise, then do all things arise. When thoughts vanish, then do all things vanish.",
        "Where there are humans, you'll find flies. And Buddhas.",
        "Only the hand that erases can write the true thing.",
        "Life is a journey. Time is a river. The door is ajar.",
        "The mind is everything. What you think you become.",
        "No snowflake ever falls in the wrong place.",
        "When you try to stay on the surface of the water, you sink; but when you try to sink, you float.",
        "The true miracle is not walking on water or walking in air, but simply walking on this earth.",
        "Zen is not some kind of excitement, but concentration on our usual everyday routine.",
        "To seek is to suffer. To seek nothing is bliss.",
        "Sleep is the best meditation.",
        "Before you speak, let your words pass through three gates: Is it true? Is it necessary? Is it kind?",
        "No one saves us but ourselves. No one can and no one may. We ourselves must walk the path.",
        "Every morning we are born again. What we do today matters most.",
        "If the problem can be solved, why worry? If the problem cannot be solved, worrying will do you no good."
    ]
    
    return random.choice(zen_quotes)

def get_guided_meditation_text(duration_minutes: int = 5, focus: str = "breath") -> str:
    """
    Get text for a guided meditation based on duration and focus.
    
    Args:
        duration_minutes: Length of meditation in minutes
        focus: Focus area for the meditation (breath, body, compassion, etc.)
        
    Returns:
        String with guided meditation instructions
    """
    # Basic structure for a guided meditation
    meditations = {
        "breath": {
            "title": "Mindful Breathing",
            "intro": "This meditation focuses on using the breath as an anchor for awareness.",
            "instructions": [
                "Find a comfortable seated position with your back straight but not rigid.",
                "Close your eyes or maintain a soft gaze.",
                "Take a few deep breaths, then allow your breathing to return to its natural rhythm.",
                "Focus your attention on the sensation of breathing - the air moving in and out, the rising and falling of your chest or abdomen.",
                "When your mind wanders, gently recognize this and return your focus to your breath without judgment.",
                "Continue this practice, returning to your breath each time your attention drifts."
            ],
            "closing": "As this meditation comes to a close, gradually expand your awareness to the space around you, and when you're ready, gently open your eyes."
        },
        "body": {
            "title": "Body Scan Meditation",
            "intro": "This practice helps you develop awareness of physical sensations throughout your body.",
            "instructions": [
                "Lie down or sit in a comfortable position where you can remain still.",
                "Close your eyes and bring awareness to your body as a whole.",
                "Begin at your feet, noticing any sensations present without trying to change them.",
                "Slowly move your attention upward through your legs, torso, arms, and head.",
                "Pay particular attention to areas of tension or discomfort, breathing into them with acceptance.",
                "If your mind wanders, gently bring it back to the part of the body you were focusing on."
            ],
            "closing": "Take a final deep breath, feeling your entire body, and bring gentle movement back to your fingers and toes before opening your eyes."
        },
        "compassion": {
            "title": "Loving-Kindness Meditation",
            "intro": "This meditation cultivates feelings of goodwill, kindness, and compassion toward yourself and others.",
            "instructions": [
                "Sit comfortably with your eyes closed and take a few deep breaths.",
                "Begin by directing kind thoughts toward yourself: 'May I be happy. May I be healthy. May I be safe. May I live with ease.'",
                "Next, bring to mind someone you care about deeply and extend these same wishes to them.",
                "Continue expanding this circle of compassion to include friends, neutral acquaintances, difficult people, and eventually all beings.",
                "Notice any resistance that arises without judgment, and return to the phrases.",
                "Feel the warmth of compassion spreading throughout your body and mind."
            ],
            "closing": "As you prepare to end this practice, know that you can return to these feelings of loving-kindness anytime throughout your day."
        }
    }
    
    # Default to breath meditation if the requested focus isn't available
    meditation = meditations.get(focus, meditations["breath"])
    
    # Construct the text
    meditation_text = f"# {meditation['title']} ({duration_minutes} minutes)\n\n"
    meditation_text += f"## Introduction\n{meditation['intro']}\n\n"
    meditation_text += "## Instructions\n"
    
    for i, instruction in enumerate(meditation['instructions'], 1):
        meditation_text += f"{i}. {instruction}\n"
    
    meditation_text += f"\n## Closing\n{meditation['closing']}"
    
    return meditation_text

def get_zen_garden_html(garden_data=None, mode="view"):
    """
    Returns HTML/CSS/JS code for the interactive Zen Garden.
    
    Args:
        garden_data: Optional dictionary containing existing garden configuration
        mode: Either "view" (just view the garden) or "edit" (allow interaction)
        
    Returns:
        HTML string with the interactive Zen Garden
    """
    if garden_data is None:
        garden_data = create_default_garden()
    
    # Simple visualization of the garden state without interactive components
    html = """
    <style>
    .zen-garden-container {
        display: flex;
        flex-direction: column;
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .zen-garden {
        width: 100%;
        height: 400px;
        background-color: #F8F6E9;
        border-radius: 10px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .sand {
        width: 100%;
        height: 100%;
        position: absolute;
        top: 0;
        left: 0;
        background-color: #F0E9D2;
    }
    
    .sand.waves {
        background-image: radial-gradient(circle at 1px 1px, #E9E0C9 1px, transparent 0);
        background-size: 16px 16px;
    }
    
    .sand.lines {
        background-image: linear-gradient(90deg, transparent, transparent 50%, #E9E0C9 50%, #E9E0C9 100%);
        background-size: 20px 20px;
    }
    
    .sand.circles {
        background-image: 
            radial-gradient(circle at 50% 50%, #E9E0C9 0%, transparent 10%, transparent 100%),
            radial-gradient(circle at 50% 50%, #E9E0C9 0%, transparent 15%, transparent 100%),
            radial-gradient(circle at 50% 50%, #E9E0C9 0%, transparent 20%, transparent 100%);
        background-size: 120px 120px, 90px 90px, 60px 60px;
        background-position: 0 0, 30px 30px, 60px 60px;
    }
    
    .stone {
        position: absolute;
        border-radius: 50%;
        background-color: #928E85;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stone.round {
        border-radius: 50%;
        background-color: #787167;
    }
    
    .stone.rough {
        border-radius: 40% 60% 40% 60%;
        background-color: #6E655C;
    }
    
    .stone.flat {
        border-radius: 30%;
        background-color: #847E75;
        transform: scale(1, 0.4);
    }
    
    .plant {
        position: absolute;
        width: 30px;
        height: 30px;
    }
    
    .plant.bonsai {
        background-color: #4A6741;
        clip-path: polygon(50% 0%, 70% 50%, 50% 70%, 30% 50%);
    }
    
    .plant.bamboo {
        background-color: #4A6741;
        clip-path: polygon(40% 0%, 40% 100%, 45% 100%, 45% 0%, 55% 10%, 55% 100%, 60% 100%, 60% 10%);
    }
    
    .decoration {
        position: absolute;
        width: 40px;
        height: 40px;
    }
    
    .decoration.lantern {
        background-color: #E8C596;
        clip-path: polygon(45% 0%, 45% 15%, 35% 15%, 35% 25%, 65% 25%, 65% 15%, 55% 15%, 55% 0%, 35% 75%, 65% 75%, 65% 85%, 35% 85%, 45% 85%, 45% 100%, 55% 100%, 55% 85%);
    }
    
    .decoration.bridge {
        background-color: #6D4C33;
        clip-path: polygon(5% 60%, 95% 60%, 95% 70%, 5% 70%, 5% 60%, 20% 50%, 80% 50%, 95% 60%);
    }
    
    .meditation-timer {
        width: 100%;
        background-color: #F8F6E9;
        border-radius: 10px;
        padding: 15px;
        margin-top: 15px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    
    .timer-display {
        font-size: 2.5rem;
        font-weight: 300;
        color: #5D534A;
        margin: 15px 0;
    }
    
    .timer-controls {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 15px;
    }
    
    .timer-button {
        background-color: #FFFFFF;
        border: 1px solid #E0D6C2;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .timer-button.primary {
        background-color: #4361EE;
        color: white;
        border-color: #4361EE;
        padding: 6px 20px;
    }
    
    .breathing-guide {
        width: 80px;
        height: 80px;
        margin: 0 auto;
        position: relative;
    }
    
    .breath-indicator {
        width: 50px;
        height: 50px;
        background-color: rgba(67, 97, 238, 0.2);
        border-radius: 50%;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        animation: breathe 7s infinite ease-in-out;
    }
    
    @keyframes breathe {
        0%, 100% { transform: translate(-50%, -50%) scale(0.5); opacity: 0.2; }
        50% { transform: translate(-50%, -50%) scale(1.5); opacity: 0.6; }
    }
    </style>
    """
    
    # Add garden container
    html += """
    <div class="zen-garden-container">
        <div class="zen-garden">
    """
    
    # Add sand with pattern
    sand_pattern = garden_data.get("sand_pattern", "waves")
    html += f'<div class="sand {sand_pattern}"></div>\n'
    
    # Add stones
    for stone in garden_data.get("stones", []):
        stone_type = stone.get("type", "round")
        x = stone.get("x", 0)
        y = stone.get("y", 0)
        size = stone.get("size", 15)
        html += f'<div class="stone {stone_type}" style="left: {x}%; top: {y}%; width: {size}px; height: {size}px;"></div>\n'
    
    # Add plants
    for plant in garden_data.get("plants", []):
        plant_type = plant.get("type", "bonsai")
        x = plant.get("x", 0)
        y = plant.get("y", 0)
        html += f'<div class="plant {plant_type}" style="left: {x}%; top: {y}%;"></div>\n'
    
    # Add decorations
    for decoration in garden_data.get("decorations", []):
        decoration_type = decoration.get("type", "lantern")
        x = decoration.get("x", 0)
        y = decoration.get("y", 0)
        html += f'<div class="decoration {decoration_type}" style="left: {x}%; top: {y}%;"></div>\n'
    
    # Close garden div
    html += """
        </div>
        
        <div class="meditation-timer">
            <div>Meditation Timer</div>
            <div class="timer-display">05:00</div>
            <div class="timer-controls">
                <button class="timer-button">3 min</button>
                <button class="timer-button">5 min</button>
                <button class="timer-button">10 min</button>
                <button class="timer-button primary">Start</button>
            </div>
        </div>
    </div>
    """
    
    return html