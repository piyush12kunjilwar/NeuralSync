import streamlit as st
import pandas as pd
import datetime
import json
import os
from modules.data_processing import process_journal_entry, process_wearable_data
from modules.health_api import get_mock_wearable_data, get_available_data_types
from modules.ml_models import analyze_mood_patterns, predict_stress_level
from modules.visualization import plot_mood_trend, plot_sleep_heart_correlation
from modules.openai_helper import generate_coping_strategies
from modules.ai_coaching import (
    get_available_coaching_personas, 
    generate_coaching_advice,
    analyze_progress,
    generate_personalized_exercise
)
from modules.zen_garden import (
    get_zen_garden_html,
    create_default_garden,
    record_meditation_session,
    get_meditation_stats,
    generate_zen_wisdom,
    get_guided_meditation_text
)
from utils.privacy import encrypt_data, decrypt_data
from utils.helpers import load_user_data, save_user_data

# Custom functions for premium UI
def render_metric_card(title, value, description=None, icon=None, color="#4361EE"):
    """Render a custom metric card with premium styling."""
    icon_html = f'<span style="font-size:1.5rem; margin-right:10px;">{icon}</span>' if icon else ''
    
    st.markdown(f"""
    <div style="background-color:#EDF2F7; border-radius:10px; padding:15px; margin-bottom:20px; border-left:5px solid {color};">
        <div style="display:flex; align-items:center; margin-bottom:5px;">
            {icon_html}<span style="font-size:1.1rem; font-weight:600; color:#2D3748;">{title}</span>
        </div>
        <div style="font-size:1.8rem; font-weight:700; color:#1A202C; margin:5px 0;">{value}</div>
        <div style="font-size:0.9rem; color:#4A5568; opacity:0.8;">{description or ''}</div>
    </div>
    """, unsafe_allow_html=True)

def render_insight_card(title, content, icon=None, color="#4361EE"):
    """Render a custom insight card with premium styling."""
    icon_html = f'<span style="font-size:1.5rem; margin-right:10px;">{icon}</span>' if icon else ''
    
    st.markdown(f"""
    <div style="background-color:#EDF2F7; border-radius:10px; padding:15px; margin-bottom:20px; box-shadow:0 2px 5px rgba(0,0,0,0.05);">
        <div style="display:flex; align-items:center; margin-bottom:10px; border-bottom:1px solid #E2E8F0; padding-bottom:8px;">
            {icon_html}<span style="font-size:1.1rem; font-weight:600; color:#2D3748;">{title}</span>
        </div>
        <div style="font-size:1rem; color:#4A5568; line-height:1.5;">{content}</div>
    </div>
    """, unsafe_allow_html=True)

def render_page_title(title, subtitle=None):
    """Render a custom page title with premium styling."""
    st.markdown(f"""
    <div style="margin-bottom:2rem;">
        <h1 style="font-size:2.25rem; font-weight:700; color:#1A202C; margin-bottom:0.5rem;">{title}</h1>
        <p style="font-size:1.1rem; color:#4A5568; opacity:0.8; margin-top:0;">{subtitle or ''}</p>
        <div style="height:3px; background: linear-gradient(90deg, #4361EE 0%, #A5B4FC 100%); width:100px; margin:1rem 0;"></div>
    </div>
    """, unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="NeuroSync - Mental Health Companion",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium UI enhancements
st.markdown("""
<style>
    /* Premium fonts and styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Card styling */
    div.stButton > button:first-child {
        background-color: #4361EE;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #3A56D4;
        box-shadow: 0 4px 10px rgba(67, 97, 238, 0.3);
        transform: translateY(-2px);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #2D3748;
        background-color: #EDF2F7;
        border-radius: 6px;
        padding: 0.5rem 1rem;
    }
    
    /* Header styling */
    h1, h2, h3 {
        font-weight: 700 !important;
        letter-spacing: -0.01em;
    }
    h1 {
        font-size: 2.25rem !important;
        margin-bottom: 1.5rem !important;
        color: #1A202C;
    }
    h2 {
        font-size: 1.75rem !important;
        margin-bottom: 1rem !important;
        color: #2D3748;
    }
    h3 {
        font-size: 1.25rem !important;
        margin-bottom: 0.75rem !important;
        color: #4A5568;
    }
    
    /* Metric card styling */
    div.css-1r6slb0.e1tzin5v2 {
        background-color: #EDF2F7;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }
    section[data-testid="stSidebar"] h1 {
        color: #4361EE;
    }
    
    /* Form styling */
    div[data-baseweb="select"] {
        border-radius: 6px;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        border: none !important;
    }
    .dataframe thead th {
        background-color: #4361EE !important;
        color: white !important;
        padding: 12px 24px !important;
        border: none !important;
    }
    .dataframe tbody tr:nth-child(even) {
        background-color: #F8FAFC !important;
    }
    .dataframe tbody tr:hover {
        background-color: #EDF2F7 !important;
    }
    .dataframe td {
        padding: 8px 24px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'journal_entries' not in st.session_state:
    st.session_state.journal_entries = []
if 'wearable_data' not in st.session_state:
    st.session_state.wearable_data = []
if 'coping_strategies' not in st.session_state:
    st.session_state.coping_strategies = []
if 'coaching_history' not in st.session_state:
    st.session_state.coaching_history = []
if 'coaching_sessions' not in st.session_state:
    st.session_state.coaching_sessions = {}
if 'zen_garden_data' not in st.session_state:
    st.session_state.zen_garden_data = create_default_garden()
if 'user_authenticated' not in st.session_state:
    st.session_state.user_authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Import custom assets
import base64
import sys
import os
sys.path.append(os.path.abspath("."))
from assets.logo import get_logo_base64
from assets.brain_animation import get_brain_animation_html, get_welcome_animation

# Sidebar for navigation with custom logo
logo_base64 = get_logo_base64().strip()
st.sidebar.markdown(
    f"""
    <div style="display:flex; justify-content:center; margin-bottom:10px;">
        <img src="data:image/png;base64,{logo_base64}" width="100" />
    </div>
    """, 
    unsafe_allow_html=True
)

st.sidebar.title("NeuroSync")
st.sidebar.markdown("<p style='font-size:1.1em; font-weight:400; opacity:0.85; margin-top:-15px; margin-bottom:25px;'>Your Mental Health Companion</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Simple authentication system
if not st.session_state.user_authenticated:
    # Add login form to sidebar
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        # In a real app, we would verify credentials against a secure database
        # For demo purposes, accept any non-empty input
        if username and password:
            st.session_state.user_authenticated = True
            st.session_state.user_id = username
            # Load user data
            user_data = load_user_data(username)
            if user_data:
                st.session_state.journal_entries = user_data.get('journal_entries', [])
                st.session_state.wearable_data = user_data.get('wearable_data', [])
                st.session_state.coping_strategies = user_data.get('coping_strategies', [])
                st.session_state.coaching_history = user_data.get('coaching_history', [])
            st.sidebar.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.sidebar.error("Please enter both username and password")
    
    # Add 3D brain animation and welcome content to main area
    # Welcome animation and content
    st.markdown(get_welcome_animation(), unsafe_allow_html=True)
    
    # 3D brain animation
    st.markdown(get_brain_animation_html(), unsafe_allow_html=True)
    
    # Additional information about the app
    st.markdown("""
    <div class="login-info-container">
        <div class="login-info-card">
            <h3>About NeuroSync</h3>
            <p>NeuroSync is a privacy-first mental health companion that uses AI to provide personalized support while keeping your data secure and private.</p>
            <p>Using federated learning, all your sensitive data stays on your device - nothing is sent to external servers.</p>
        </div>
        
        <div class="login-info-card">
            <h3>Key Features</h3>
            <ul>
                <li><strong>Secure Journaling</strong> - Record thoughts and feelings with sentiment analysis</li>
                <li><strong>Wearable Integration</strong> - Connect with your fitness devices</li>
                <li><strong>AI Insights</strong> - Get personalized coping strategies</li>
                <li><strong>Privacy Protected</strong> - Your data never leaves your device</li>
            </ul>
        </div>
    </div>
    
    <style>
    .login-info-container {
        display: flex;
        gap: 20px;
        margin-top: 30px;
        margin-bottom: 30px;
        flex-wrap: wrap;
    }
    
    .login-info-card {
        flex: 1;
        min-width: 300px;
        background: white;
        border-radius: 10px;
        padding: 25px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .login-info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    .login-info-card h3 {
        color: #4361EE;
        margin-bottom: 15px;
        font-size: 1.3rem;
    }
    
    .login-info-card p, .login-info-card ul {
        color: #4A5568;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    .login-info-card ul {
        padding-left: 20px;
    }
    
    .login-info-card li {
        margin-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.sidebar.success(f"Logged in as {st.session_state.user_id}")
    if st.sidebar.button("Logout"):
        # Save user data before logging out
        if st.session_state.user_id:
            user_data = {
                'journal_entries': st.session_state.journal_entries,
                'wearable_data': st.session_state.wearable_data,
                'coping_strategies': st.session_state.coping_strategies,
                'coaching_history': st.session_state.coaching_history,
                'zen_garden_data': st.session_state.zen_garden_data
            }
            save_user_data(st.session_state.user_id, user_data)
        
        # Reset session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main application (only shown when authenticated)
if st.session_state.user_authenticated:
    # Enhanced Navigation with icons
    st.sidebar.markdown("### Main Menu")

    # Navigation options with icons
    nav_options = {
        "Dashboard": "📊",
        "Journal": "📝", 
        "Wearable Data": "⌚",
        "Analysis & Insights": "🔍",
        "Coping Strategies": "🧘",
        "AI Coaching": "🧠",
        "Zen Garden": "🪨"
    }

    # Set default nav_option if it doesn't exist in session state
    if 'nav_option' not in st.session_state:
        st.session_state.nav_option = "Dashboard"
    
    # Hidden radio for actual selection
    nav_option = st.sidebar.radio(
        "Navigation",
        list(nav_options.keys()),
        index=list(nav_options.keys()).index(st.session_state.nav_option),
        key="navigation",
        format_func=lambda x: f"{nav_options[x]} {x}"
    )
    
    # Update session state
    st.session_state.nav_option = nav_option
    
    # Dashboard page
    if nav_option == "Dashboard":
        # Custom page title with premium styling
        render_page_title(
            "Your Mental Health Dashboard", 
            "View your mental health metrics and insights in one place"
        )
        
        # Summary metrics at top
        st.markdown("""
        <div style="display:flex; gap:15px; margin-bottom:30px; flex-wrap:wrap;">
            <div style="flex:1; min-width:200px;">
                <div style="background:linear-gradient(135deg, #4361EE 0%, #3A56D4 100%); border-radius:10px; padding:20px; color:white;">
                    <div style="font-size:0.9rem; opacity:0.8;">Today's Date</div>
                    <div style="font-size:1.6rem; font-weight:600; margin:5px 0;">{}</div>
                    <div style="font-size:0.9rem; opacity:0.8;">Tracking your daily wellness</div>
                </div>
            </div>
            <div style="flex:1; min-width:200px;">
                <div style="background:linear-gradient(135deg, #4CC9F0 0%, #4361EE 100%); border-radius:10px; padding:20px; color:white;">
                    <div style="font-size:0.9rem; opacity:0.8;">Journal Entries</div>
                    <div style="font-size:1.6rem; font-weight:600; margin:5px 0;">{}</div>
                    <div style="font-size:0.9rem; opacity:0.8;">Continue your wellness journey</div>
                </div>
            </div>
            <div style="flex:1; min-width:200px;">
                <div style="background:linear-gradient(135deg, #7209B7 0%, #4361EE 100%); border-radius:10px; padding:20px; color:white;">
                    <div style="font-size:0.9rem; opacity:0.8;">Mood Score</div>
                    <div style="font-size:1.6rem; font-weight:600; margin:5px 0;">{}/10</div>
                    <div style="font-size:0.9rem; opacity:0.8;">Your latest mood rating</div>
                </div>
            </div>
        </div>
        """.format(
            datetime.datetime.now().strftime("%B %d, %Y"),
            len(st.session_state.journal_entries),
            st.session_state.journal_entries[-1].get('mood_score', 'N/A') if st.session_state.journal_entries else 'N/A'
        ), unsafe_allow_html=True)
        
        # Display summary statistics and visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h3 style='color:#4361EE; font-size:1.3rem;'>Mood Trends</h3>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom:15px; background:#EDF2F7; border-radius:10px; padding:15px;'>", unsafe_allow_html=True)
            if st.session_state.journal_entries:
                mood_data = [entry.get('mood_score', 0) for entry in st.session_state.journal_entries]
                dates = [entry.get('date', '') for entry in st.session_state.journal_entries]
                plot_mood_trend(dates, mood_data)
            else:
                st.info("Start journaling to see your mood trends")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<h3 style='color:#4361EE; font-size:1.3rem;'>Sleep & Heart Rate</h3>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom:15px; background:#EDF2F7; border-radius:10px; padding:15px;'>", unsafe_allow_html=True)
            if st.session_state.wearable_data:
                sleep_data = [entry.get('sleep_hours', 0) for entry in st.session_state.wearable_data]
                heart_data = [entry.get('avg_heart_rate', 0) for entry in st.session_state.wearable_data]
                dates = [entry.get('date', '') for entry in st.session_state.wearable_data]
                plot_sleep_heart_correlation(dates, sleep_data, heart_data)
            else:
                st.info("Connect your wearable device to see correlations")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Recent coping strategies
        st.markdown("<h3 style='color:#4361EE; font-size:1.3rem; margin-top:20px;'>Recent Coping Strategies</h3>", unsafe_allow_html=True)
        if st.session_state.coping_strategies:
            for i, strategy in enumerate(st.session_state.coping_strategies[-3:]):
                strategy_date = strategy.get('date', 'No date')
                strategy_text = strategy.get('strategy', 'No strategy available')
                
                render_insight_card(
                    f"Strategy {i+1} - {strategy_date}", 
                    strategy_text,
                    icon="🧘"
                )
        else:
            st.markdown("""
            <div style="background:#EDF2F7; border-radius:10px; padding:20px; margin-bottom:20px; text-align:center;">
                <div style="font-size:3rem; color:#A0AEC0; margin-bottom:10px;">🧠</div>
                <div style="font-size:1.1rem; font-weight:600; color:#4A5568; margin-bottom:5px;">No Coping Strategies Yet</div>
                <div style="color:#718096; margin-bottom:15px;">Visit the Coping Strategies page to generate personalized mental health strategies</div>
                <div>
                    <a href="#" style="display:inline-block; background:#4361EE; color:white; text-decoration:none; padding:8px 16px; border-radius:6px; font-weight:500;">
                        Generate Strategies
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Journal page
    elif nav_option == "Journal":
        # Custom page title with premium styling
        render_page_title(
            "Mental Health Journal", 
            "Record your thoughts, feelings, and experiences securely"
        )
        
        # Two-column layout for form and recent entries
        journal_col1, journal_col2 = st.columns([3, 2])
        
        with journal_col1:
            # Journal entry card wrapper
            st.markdown("""
            <div style="background:#EDF2F7; border-radius:15px; padding:25px; margin-bottom:20px; box-shadow:0 2px 10px rgba(0,0,0,0.05);">
                <div style="display:flex; align-items:center; margin-bottom:15px;">
                    <span style="font-size:1.5rem; margin-right:10px;">📝</span>
                    <span style="font-size:1.2rem; font-weight:600; color:#2D3748;">New Journal Entry</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Journal entry form
            with st.form("journal_entry_form"):
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                entry_date = st.date_input("Date", datetime.datetime.now())
                entry_title = st.text_input("Title", placeholder="Give your entry a title...")
                entry_content = st.text_area("How are you feeling today?", height=200, placeholder="Write freely about your thoughts, feelings, and experiences...")
                
                # Mood slider with better styling
                st.markdown("<div style='margin:15px 0 5px;'><b>Rate your mood</b></div>", unsafe_allow_html=True)
                mood_labels = {1: "Very Low", 5: "Neutral", 10: "Excellent"}
                mood_score = st.slider(
                    "Mood",
                    1, 10, 5,
                    label_visibility="collapsed",
                    help="1 = Very low, 10 = Excellent"
                )
                
                # Visual indicator for mood
                mood_color = "#F56565" if mood_score <= 3 else "#4361EE" if mood_score <= 7 else "#48BB78"
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
                    <span style="color:#718096; font-size:0.9rem;">Very Low</span>
                    <span style="color:{mood_color}; font-weight:600; font-size:1.1rem;">{mood_score}/10</span>
                    <span style="color:#718096; font-size:0.9rem;">Excellent</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Stress level
                st.markdown("<div style='margin:15px 0 5px;'><b>Rate your stress level</b></div>", unsafe_allow_html=True)
                stress_level = st.slider(
                    "Stress",
                    1, 10, 5,
                    label_visibility="collapsed",
                    help="1 = None, 10 = Extreme"
                )
                
                # Sleep quality
                st.markdown("<div style='margin:15px 0 5px;'><b>Rate your sleep quality</b></div>", unsafe_allow_html=True)
                sleep_quality = st.slider(
                    "Sleep",
                    1, 10, 5,
                    label_visibility="collapsed",
                    help="1 = Poor, 10 = Excellent"
                )
                
                # Additional factors with better styling
                st.markdown("<div style='margin:15px 0 10px;'><b>Additional wellness factors</b></div>", unsafe_allow_html=True)
                
                factor_col1, factor_col2 = st.columns(2)
                with factor_col1:
                    exercise = st.checkbox("Exercise today")
                    meditation = st.checkbox("Meditation today")
                with factor_col2:
                    social_interaction = st.checkbox("Social interaction today")
                    outdoor_time = st.checkbox("Time outdoors today")
                
                # Submit button
                submitted = st.form_submit_button("Save Journal Entry")
                
                if submitted:
                    if entry_content:
                        # Process journal entry with client-side analysis
                        processed_entry = process_journal_entry(
                            date=entry_date.strftime("%Y-%m-%d"),
                            title=entry_title,
                            content=entry_content,
                            mood_score=mood_score,
                            stress_level=stress_level,
                            sleep_quality=sleep_quality,
                            exercise=exercise,
                            meditation=meditation,
                            social_interaction=social_interaction,
                            outdoor_time=outdoor_time
                        )
                        
                        # Encrypt sensitive data before storing (in a real app)
                        # Here we simulate encryption for demonstration
                        encrypted_entry = encrypt_data(processed_entry)
                        
                        # Store the entry
                        st.session_state.journal_entries.append(encrypted_entry)
                        
                        # Save user data
                        user_data = {
                            'journal_entries': st.session_state.journal_entries,
                            'wearable_data': st.session_state.wearable_data,
                            'coping_strategies': st.session_state.coping_strategies
                        }
                        save_user_data(st.session_state.user_id, user_data)
                        
                        st.success("Journal entry saved successfully!")
                    else:
                        st.error("Please write something in your journal entry")
            
            # End of card wrapper
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Privacy notice
            st.markdown("""
            <div style="background:#EBF8FF; border-radius:10px; padding:15px; border-left:4px solid #4361EE; margin-top:20px;">
                <div style="display:flex; align-items:center; margin-bottom:5px;">
                    <span style="font-size:1.2rem; margin-right:10px;">🔐</span>
                    <span style="font-weight:600; color:#2C5282;">Privacy Commitment</span>
                </div>
                <p style="margin:0; color:#2A4365; font-size:0.9rem; line-height:1.5;">
                    Your journal entries are processed locally and encrypted. 
                    At NeuroSync, we prioritize your privacy and security - your personal data never leaves your device.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with journal_col2:
            # Recent activity and streaks
            if st.session_state.journal_entries:
                entry_count = len(st.session_state.journal_entries)
                streak_days = min(entry_count, 7)  # Simplified - in real app would calculate actual streaks
                
                st.markdown(f"""
                <div style="background:linear-gradient(135deg, #4361EE 0%, #3A56D4 100%); border-radius:15px; padding:20px; color:white; margin-bottom:20px;">
                    <div style="font-size:1rem; font-weight:500; margin-bottom:10px;">Journal Activity</div>
                    <div style="font-size:2rem; font-weight:700; margin-bottom:5px;">{entry_count}</div>
                    <div style="font-size:0.9rem; opacity:0.8;">Total entries</div>
                    
                    <div style="height:1px; background:rgba(255,255,255,0.2); margin:15px 0;"></div>
                    
                    <div style="font-size:1rem; font-weight:500; margin-bottom:10px;">Current Streak</div>
                    <div style="font-size:2rem; font-weight:700; margin-bottom:5px;">{streak_days} days</div>
                    <div style="font-size:0.9rem; opacity:0.8;">Keep going! Consistency matters.</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Journal insights
            st.markdown("""
            <div style="background:#EDF2F7; border-radius:15px; padding:20px; margin-bottom:20px;">
                <div style="font-size:1.1rem; font-weight:600; color:#2D3748; margin-bottom:15px;">
                    Journaling Benefit
                </div>
                <p style="margin:0 0 15px; color:#4A5568; line-height:1.5;">
                    Regular journaling has been shown to reduce stress, improve immune function, and boost mood.
                </p>
                <div style="font-size:0.9rem; color:#4361EE;">Source: University of Rochester Medical Center</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Display previous entries with better styling
        st.markdown("<h3 style='margin-top:30px; font-size:1.3rem; color:#4361EE;'>Previous Entries</h3>", unsafe_allow_html=True)
        
        if st.session_state.journal_entries:
            # Sort entries by date (newest first)
            sorted_entries = sorted(
                st.session_state.journal_entries, 
                key=lambda x: x.get('date', ''), 
                reverse=True
            )
            
            for i, entry in enumerate(sorted_entries):
                # Decrypt the entry (in a real app)
                decrypted_entry = decrypt_data(entry)
                entry_date = decrypted_entry.get('date', 'No date')
                entry_title = decrypted_entry.get('title', 'No title')
                
                with st.expander(f"{entry_date} - {entry_title}"):
                    # Entry metadata with icons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        mood = decrypted_entry.get('mood_score', 'N/A')
                        mood_color = "#F56565" if mood <= 3 else "#4361EE" if mood <= 7 else "#48BB78"
                        st.markdown(f"""
                        <div style="padding:10px; background:#F7FAFC; border-radius:8px; text-align:center;">
                            <div style="color:#718096; font-size:0.9rem;">Mood</div>
                            <div style="font-size:1.5rem; font-weight:700; color:{mood_color};">{mood}/10</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        stress = decrypted_entry.get('stress_level', 'N/A')
                        stress_color = "#48BB78" if stress <= 3 else "#4361EE" if stress <= 7 else "#F56565"
                        st.markdown(f"""
                        <div style="padding:10px; background:#F7FAFC; border-radius:8px; text-align:center;">
                            <div style="color:#718096; font-size:0.9rem;">Stress</div>
                            <div style="font-size:1.5rem; font-weight:700; color:{stress_color};">{stress}/10</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        sleep = decrypted_entry.get('sleep_quality', 'N/A')
                        sleep_color = "#F56565" if sleep <= 3 else "#4361EE" if sleep <= 7 else "#48BB78"
                        st.markdown(f"""
                        <div style="padding:10px; background:#F7FAFC; border-radius:8px; text-align:center;">
                            <div style="color:#718096; font-size:0.9rem;">Sleep</div>
                            <div style="font-size:1.5rem; font-weight:700; color:{sleep_color};">{sleep}/10</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Journal content
                    st.markdown(f"""
                    <div style="margin-top:15px; padding:15px; background:#F7FAFC; border-radius:8px; line-height:1.6;">
                        {decrypted_entry.get('content', 'No content')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Additional factors as pills
                    factors = []
                    if decrypted_entry.get('exercise', False):
                        factors.append("Exercise")
                    if decrypted_entry.get('meditation', False):
                        factors.append("Meditation") 
                    if decrypted_entry.get('social_interaction', False):
                        factors.append("Social Interaction")
                    if decrypted_entry.get('outdoor_time', False):
                        factors.append("Outdoor Time")
                    
                    if factors:
                        st.markdown("<div style='margin-top:15px;'>", unsafe_allow_html=True)
                        for factor in factors:
                            st.markdown(f"""
                            <span style="display:inline-block; background:#E6FFFA; color:#319795; padding:5px 10px; 
                                          border-radius:15px; font-size:0.8rem; margin-right:8px; margin-bottom:8px;">
                                {factor}
                            </span>
                            """, unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
        else:
            st.markdown("""
            <div style="background:#EDF2F7; border-radius:10px; padding:30px; margin-bottom:20px; text-align:center;">
                <div style="font-size:3rem; color:#A0AEC0; margin-bottom:10px;">📝</div>
                <div style="font-size:1.2rem; font-weight:600; color:#4A5568; margin-bottom:10px;">No Journal Entries Yet</div>
                <div style="color:#718096; margin-bottom:15px;">Start writing today to track your mental health journey</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Wearable Data page
    elif nav_option == "Wearable Data":
        # Custom page title with premium styling
        render_page_title(
            "Wearable Health Data", 
            "Connect and analyze data from your wearable devices"
        )
        
        # Create tabs for different wearable data sections
        wearable_tabs = st.tabs([
            "📱 Connect Device", 
            "📊 Historical Data", 
            "⚡ Real-Time Monitoring",
            "⚙️ Settings"
        ])
        
        # Tab 1: Connect Device
        with wearable_tabs[0]:
            st.markdown("<div style='background:#EDF2F7; border-radius:10px; padding:20px; margin-bottom:20px;'>", unsafe_allow_html=True)
            
            # In a real app, we would implement actual wearable API connections
            # For this demo, we'll use simulated data
            st.info("Note: This is a demo using simulated wearable data. In a real app, you would connect to actual device APIs.")
            
            device_col1, device_col2 = st.columns([3, 2])
            
            with device_col1:
                st.subheader("Connect Your Device")
                
                # Get list of devices from our enhanced function
                devices = get_device_list()
                
                # Device selection with more options
                data_source = st.selectbox(
                    "Select your wearable device/platform",
                    devices
                )
                
                # Get available metrics for the selected device
                available_metrics = get_available_data_types(data_source)
                
                # Show what data can be imported
                st.markdown(f"<p style='margin-top:15px;'><strong>Available metrics for {data_source}:</strong></p>", unsafe_allow_html=True)
                
                # More user-friendly metric selection with columns
                metric_cols = st.columns(2)
                selected_metrics = []
                
                for i, metric in enumerate(available_metrics):
                    col_idx = i % 2
                    with metric_cols[col_idx]:
                        if st.checkbox(metric, value=metric in ["Heart Rate", "Sleep Data"], key=f"metric_{metric}"):
                            selected_metrics.append(metric)
                
                # Connection button with better styling
                st.markdown("<div style='margin-top:20px;'>", unsafe_allow_html=True)
                if st.button("Connect and Import Data", use_container_width=True):
                    with st.spinner(f"Connecting to {data_source}..."):
                        # In a real app, this would connect to the actual API
                        # and import real data with proper authentication
                        
                        # For demo, generate mock data for the past week
                        new_data = []
                        for i in range(7):
                            date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
                            wearable_data = get_mock_wearable_data(date, selected_metrics)
                            processed_data = process_wearable_data(wearable_data)
                            new_data.append(processed_data)
                        
                        # Add the new data to our session state
                        st.session_state.wearable_data.extend(new_data)
                        
                        # Save user data
                        user_data = {
                            'journal_entries': st.session_state.journal_entries,
                            'wearable_data': st.session_state.wearable_data,
                            'coping_strategies': st.session_state.coping_strategies
                        }
                        save_user_data(st.session_state.user_id, user_data)
                        
                        st.success(f"Successfully imported data from {data_source}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            with device_col2:
                # Show device image based on selection
                device_images = {
                    "Apple Watch": "https://images.unsplash.com/photo-1551816230-ef5deaed4a26?auto=format&fit=crop&w=300&h=300",
                    "Fitbit": "https://images.unsplash.com/photo-1575311373937-040b8e1fd6b5?auto=format&fit=crop&w=300&h=300",
                    "Garmin": "https://images.unsplash.com/photo-1616924416635-3d6b617118ff?auto=format&fit=crop&w=300&h=300",
                    "Samsung Galaxy Watch": "https://images.unsplash.com/photo-1617043786394-f977fa12eddf?auto=format&fit=crop&w=300&h=300",
                    "Oura Ring": "https://images.unsplash.com/photo-1628935283668-073122b2d8b6?auto=format&fit=crop&w=300&h=300"
                }
                
                # Display image if available, else a generic one
                if data_source in device_images:
                    st.image(device_images[data_source], use_column_width=True)
                else:
                    st.image("https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?auto=format&fit=crop&w=300&h=300", use_column_width=True)
                
                st.markdown(f"<p style='text-align:center; margin-top:10px;'><strong>{data_source}</strong></p>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Device connection instructions
            st.markdown("<div style='background:#E6FFFA; border-radius:10px; padding:20px; margin-top:20px;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:#2C7A7B;'>How to Connect Your Device</h4>", unsafe_allow_html=True)
            
            connect_col1, connect_col2 = st.columns(2)
            
            with connect_col1:
                st.markdown("""
                1. **Enable Bluetooth** on your phone and wearable device
                2. **Open your device's app** (Apple Health, Fitbit, etc.)
                3. **Grant permissions** to NeuroSync in your device settings
                4. **Select metrics** you want to share with NeuroSync
                """)
            
            with connect_col2:
                st.markdown("""
                5. **Sync your device** to ensure latest data is available
                6. **Click "Connect"** above and authorize the connection
                7. **Review privacy settings** to control data sharing
                8. **Data is processed locally** for maximum privacy
                """)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Tab 2: Historical Data
        with wearable_tabs[1]:
            if not st.session_state.wearable_data:
                # Show empty state if no data
                st.markdown("""
                <div style="background:#EDF2F7; border-radius:10px; padding:30px; margin:20px 0; text-align:center;">
                    <div style="font-size:3rem; color:#A0AEC0; margin-bottom:20px;">📊</div>
                    <div style="font-size:1.2rem; font-weight:600; color:#4A5568; margin-bottom:10px;">No Wearable Data Available</div>
                    <div style="color:#718096; margin-bottom:20px;">Connect your wearable device to see your health metrics and trends over time.</div>
                    <div>
                        <button style="background:#4361EE; color:white; border:none; padding:8px 16px; border-radius:4px; font-weight:500; cursor:pointer;">
                            Go to Connect Device Tab
                        </button>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Filter and date range controls
                st.markdown("<div style='background:#EDF2F7; border-radius:10px; padding:20px; margin-bottom:20px;'>", unsafe_allow_html=True)
                
                filter_col1, filter_col2 = st.columns([3, 1])
                
                with filter_col1:
                    # Date range selector
                    date_options = ["Last 7 days", "Last 30 days", "Last 90 days", "All time", "Custom range"]
                    date_range = st.selectbox("Select time period", date_options)
                    
                    # If custom range, show date pickers
                    if date_range == "Custom range":
                        custom_col1, custom_col2 = st.columns(2)
                        with custom_col1:
                            start_date = st.date_input("Start date", datetime.datetime.now() - datetime.timedelta(days=7))
                        with custom_col2:
                            end_date = st.date_input("End date", datetime.datetime.now())
                
                with filter_col2:
                    # Add refresh button
                    st.markdown("<div style='margin-top:25px;'>", unsafe_allow_html=True)
                    if st.button("Refresh Data", use_container_width=True):
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Convert to DataFrame for display and analysis
                df = pd.DataFrame(st.session_state.wearable_data)
                
                # Sort by date (newest first)
                df = df.sort_values(by='date', ascending=False)
                
                # Apply date filtering
                if date_range == "Last 7 days":
                    cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
                    df = df[df['date'] >= cutoff_date]
                elif date_range == "Last 30 days":
                    cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
                    df = df[df['date'] >= cutoff_date]
                elif date_range == "Last 90 days":
                    cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=90)).strftime("%Y-%m-%d")
                    df = df[df['date'] >= cutoff_date]
                elif date_range == "Custom range":
                    df = df[(df['date'] >= start_date.strftime("%Y-%m-%d")) & 
                            (df['date'] <= end_date.strftime("%Y-%m-%d"))]
                
                # Reverse for chronological order in charts
                chart_df = df.sort_values(by='date')
                
                # Wellness Score (if available)
                if 'wellness_score' in df.columns and df['wellness_score'].sum() > 0:
                    latest_score = df.iloc[0]['wellness_score'] if not df.empty else 0
                    
                    # Create a gauge chart for wellness score
                    st.markdown("<h3 style='color:#4361EE; margin-top:20px;'>Wellness Score</h3>", unsafe_allow_html=True)
                    
                    # Score color based on value
                    score_color = "#F56565" if latest_score < 50 else "#4361EE" if latest_score < 75 else "#48BB78"
                    
                    # Display score as a big number with description
                    st.markdown(f"""
                    <div style="background:white; border-radius:10px; padding:20px; margin-bottom:20px; box-shadow:0 2px 10px rgba(0,0,0,0.05);">
                        <div style="display:flex; align-items:center; justify-content:space-between;">
                            <div>
                                <div style="font-size:0.9rem; color:#718096;">Current Wellness Score</div>
                                <div style="font-size:2rem; font-weight:600; color:{score_color};">{int(latest_score)}/100</div>
                                <div style="font-size:0.9rem; color:#718096;">Based on your sleep, activity, and heart metrics</div>
                            </div>
                            <div style="width:120px; height:120px; display:flex; align-items:center; justify-content:center; position:relative;">
                                <div style="position:absolute; width:120px; height:120px; border-radius:50%; background:conic-gradient(
                                    {score_color} 0% {latest_score}%, 
                                    #EDF2F7 {latest_score}% 100%
                                ); transform:rotate(-90deg);">
                                </div>
                                <div style="width:90px; height:90px; background:white; border-radius:50%; position:absolute; display:flex; align-items:center; justify-content:center;">
                                    <span style="transform:rotate(90deg); font-weight:600; color:{score_color};">{int(latest_score)}%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show trend if we have multiple days
                    if len(chart_df) > 1 and 'wellness_score' in chart_df.columns:
                        st.markdown("<p><strong>Wellness Score Trend</strong></p>", unsafe_allow_html=True)
                        
                        wellness_df = pd.DataFrame({
                            'Date': chart_df['date'],
                            'Wellness Score': chart_df['wellness_score']
                        })
                        
                        st.line_chart(wellness_df.set_index('Date'))
                
                # Display health metrics in collapsible sections
                metric_groups = {
                    "Heart Health": ["avg_heart_rate", "resting_heart_rate", "heart_rate_variability", "blood_oxygen"],
                    "Sleep": ["sleep_hours", "deep_sleep_percentage", "rem_sleep_percentage", "sleep_disruptions", "sleep_efficiency"],
                    "Activity": ["steps", "active_calories", "activity_minutes", "distance_km", "floors_climbed"],
                    "Stress & Recovery": ["stress_score", "body_battery", "recovery_score", "strain_score"]
                }
                
                # Iterate through metric groups
                for group_name, metrics in metric_groups.items():
                    # Check if we have any of these metrics
                    has_metrics = any(metric in df.columns for metric in metrics)
                    
                    if has_metrics:
                        with st.expander(f"{group_name} Metrics", expanded=group_name == "Heart Health"):
                            # Heart health metrics
                            if group_name == "Heart Health":
                                # Heart rate trend chart
                                if 'avg_heart_rate' in df.columns and df['avg_heart_rate'].sum() > 0:
                                    st.markdown("<p><strong>Heart Rate Trends</strong></p>", unsafe_allow_html=True)
                                    
                                    heart_cols = ['avg_heart_rate', 'resting_heart_rate']
                                    heart_col_names = ['Average Heart Rate', 'Resting Heart Rate']
                                    
                                    # Add HRV if available
                                    if 'heart_rate_variability' in df.columns and df['heart_rate_variability'].sum() > 0:
                                        heart_cols.append('heart_rate_variability')
                                        heart_col_names.append('Heart Rate Variability')
                                    
                                    # Create chart data
                                    hr_data = {'Date': chart_df['date']}
                                    for i, col in enumerate(heart_cols):
                                        if col in chart_df.columns:
                                            hr_data[heart_col_names[i]] = chart_df[col]
                                    
                                    # Create DataFrame and plot
                                    heart_df = pd.DataFrame(hr_data)
                                    st.line_chart(heart_df.set_index('Date'))
                                
                                # Blood oxygen if available
                                if 'blood_oxygen' in df.columns and df['blood_oxygen'].sum() > 0:
                                    st.markdown("<p><strong>Blood Oxygen Saturation</strong></p>", unsafe_allow_html=True)
                                    
                                    oxygen_df = pd.DataFrame({
                                        'Date': chart_df['date'],
                                        'SpO2 (%)': chart_df['blood_oxygen']
                                    })
                                    
                                    st.line_chart(oxygen_df.set_index('Date'))
                            
                            # Sleep metrics
                            elif group_name == "Sleep":
                                if 'sleep_hours' in df.columns and df['sleep_hours'].sum() > 0:
                                    st.markdown("<p><strong>Sleep Duration & Quality</strong></p>", unsafe_allow_html=True)
                                    
                                    # Create sleep DataFrame
                                    sleep_data = {'Date': chart_df['date'], 'Sleep Hours': chart_df['sleep_hours']}
                                    
                                    # Add other sleep metrics if available
                                    if 'deep_sleep_percentage' in chart_df.columns:
                                        sleep_data['Deep Sleep %'] = chart_df['deep_sleep_percentage']
                                    if 'rem_sleep_percentage' in chart_df.columns:
                                        sleep_data['REM Sleep %'] = chart_df['rem_sleep_percentage']
                                    if 'sleep_efficiency' in chart_df.columns:
                                        sleep_data['Sleep Efficiency'] = chart_df['sleep_efficiency']
                                        
                                    sleep_df = pd.DataFrame(sleep_data)
                                    
                                    # Plot sleep hours
                                    st.bar_chart(sleep_df.set_index('Date')['Sleep Hours'])
                                    
                                    # Plot sleep composition if available
                                    if 'Deep Sleep %' in sleep_df.columns and 'REM Sleep %' in sleep_df.columns:
                                        st.markdown("<p><strong>Sleep Composition</strong></p>", unsafe_allow_html=True)
                                        st.line_chart(sleep_df.set_index('Date')[['Deep Sleep %', 'REM Sleep %']])
                            
                            # Activity metrics
                            elif group_name == "Activity":
                                if 'steps' in df.columns and df['steps'].sum() > 0:
                                    st.markdown("<p><strong>Daily Steps</strong></p>", unsafe_allow_html=True)
                                    
                                    steps_df = pd.DataFrame({
                                        'Date': chart_df['date'],
                                        'Steps': chart_df['steps']
                                    })
                                    
                                    st.bar_chart(steps_df.set_index('Date'))
                                
                                # Show other activity metrics if available
                                if 'active_calories' in df.columns and df['active_calories'].sum() > 0:
                                    st.markdown("<p><strong>Active Calories</strong></p>", unsafe_allow_html=True)
                                    
                                    calories_df = pd.DataFrame({
                                        'Date': chart_df['date'],
                                        'Calories': chart_df['active_calories']
                                    })
                                    
                                    st.bar_chart(calories_df.set_index('Date'))
                            
                            # Stress & Recovery metrics
                            elif group_name == "Stress & Recovery":
                                # Check for stress score
                                if 'stress_score' in df.columns and df['stress_score'].sum() > 0:
                                    st.markdown("<p><strong>Stress Levels</strong></p>", unsafe_allow_html=True)
                                    
                                    stress_df = pd.DataFrame({
                                        'Date': chart_df['date'],
                                        'Stress Score': chart_df['stress_score']
                                    })
                                    
                                    st.line_chart(stress_df.set_index('Date'))
                                
                                # Check for recovery metrics
                                recovery_metrics = []
                                recovery_names = []
                                
                                if 'body_battery' in df.columns and df['body_battery'].sum() > 0:
                                    recovery_metrics.append('body_battery')
                                    recovery_names.append('Body Battery')
                                
                                if 'recovery_score' in df.columns and df['recovery_score'].sum() > 0:
                                    recovery_metrics.append('recovery_score')
                                    recovery_names.append('Recovery Score')
                                
                                if recovery_metrics:
                                    st.markdown("<p><strong>Recovery Metrics</strong></p>", unsafe_allow_html=True)
                                    
                                    recovery_data = {'Date': chart_df['date']}
                                    for i, metric in enumerate(recovery_metrics):
                                        recovery_data[recovery_names[i]] = chart_df[metric]
                                    
                                    recovery_df = pd.DataFrame(recovery_data)
                                    st.line_chart(recovery_df.set_index('Date'))
                
                # Raw data table (collapsible)
                with st.expander("View Raw Data", expanded=False):
                    st.dataframe(df)
        
        # Tab 3: Real-Time Monitoring
        with wearable_tabs[2]:
            st.markdown("<div style='background:#EDF2F7; border-radius:10px; padding:20px; margin-bottom:20px;'>", unsafe_allow_html=True)
            
            # Device selection for real-time monitoring
            rt_col1, rt_col2 = st.columns([3, 1])
            
            with rt_col1:
                # Device selection
                rt_device = st.selectbox(
                    "Select device for real-time monitoring",
                    get_device_list(),
                    key="rt_device"
                )
                
                # Refresh rate
                refresh_rates = ["5 seconds", "10 seconds", "30 seconds", "1 minute"]
                refresh_rate = st.select_slider(
                    "Update frequency",
                    options=refresh_rates,
                    value="10 seconds"
                )
            
            with rt_col2:
                st.markdown("<div style='margin-top:25px;'>", unsafe_allow_html=True)
                # Start/stop button
                if 'rt_monitoring' not in st.session_state:
                    st.session_state.rt_monitoring = False
                
                if st.session_state.rt_monitoring:
                    if st.button("Stop Monitoring", use_container_width=True):
                        st.session_state.rt_monitoring = False
                else:
                    if st.button("Start Monitoring", use_container_width=True):
                        st.session_state.rt_monitoring = True
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Real-time data display
            if st.session_state.rt_monitoring:
                # Get real-time metrics
                rt_data = get_real_time_metrics(rt_device)
                
                # Create 3-column layout for metrics
                rt_metrics_col1, rt_metrics_col2, rt_metrics_col3 = st.columns(3)
                
                with rt_metrics_col1:
                    # Heart rate display
                    if 'heart_rate' in rt_data:
                        hr_color = "#48BB78" if rt_data['heart_rate'] < 80 else "#F6AD55" if rt_data['heart_rate'] < 100 else "#F56565"
                        st.markdown(f"""
                        <div style="background:white; border-radius:10px; padding:15px; margin-bottom:15px; box-shadow:0 2px 10px rgba(0,0,0,0.05);">
                            <div style="font-size:0.9rem; color:#718096;">Heart Rate</div>
                            <div style="font-size:2rem; font-weight:600; color:{hr_color};">{rt_data['heart_rate']}</div>
                            <div style="font-size:0.9rem; color:#718096;">BPM • {rt_data.get('heart_rate_zone', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Respiratory rate if available
                    if 'respiratory_rate' in rt_data:
                        st.markdown(f"""
                        <div style="background:white; border-radius:10px; padding:15px; margin-bottom:15px; box-shadow:0 2px 10px rgba(0,0,0,0.05);">
                            <div style="font-size:0.9rem; color:#718096;">Respiratory Rate</div>
                            <div style="font-size:2rem; font-weight:600; color:#4361EE;">{rt_data['respiratory_rate']}</div>
                            <div style="font-size:0.9rem; color:#718096;">breaths/min</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with rt_metrics_col2:
                    # Blood oxygen if available
                    if 'blood_oxygen' in rt_data:
                        spo2_color = "#F56565" if rt_data['blood_oxygen'] < 90 else "#F6AD55" if rt_data['blood_oxygen'] < 95 else "#48BB78"
                        st.markdown(f"""
                        <div style="background:white; border-radius:10px; padding:15px; margin-bottom:15px; box-shadow:0 2px 10px rgba(0,0,0,0.05);">
                            <div style="font-size:0.9rem; color:#718096;">Blood Oxygen</div>
                            <div style="font-size:2rem; font-weight:600; color:{spo2_color};">{rt_data['blood_oxygen']}%</div>
                            <div style="font-size:0.9rem; color:#718096;">SpO2</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # HRV if available
                    if 'hrv' in rt_data:
                        st.markdown(f"""
                        <div style="background:white; border-radius:10px; padding:15px; margin-bottom:15px; box-shadow:0 2px 10px rgba(0,0,0,0.05);">
                            <div style="font-size:0.9rem; color:#718096;">Heart Rate Variability</div>
                            <div style="font-size:2rem; font-weight:600; color:#4361EE;">{rt_data['hrv']}</div>
                            <div style="font-size:0.9rem; color:#718096;">ms</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with rt_metrics_col3:
                    # Steps if available
                    if 'steps' in rt_data:
                        st.markdown(f"""
                        <div style="background:white; border-radius:10px; padding:15px; margin-bottom:15px; box-shadow:0 2px 10px rgba(0,0,0,0.05);">
                            <div style="font-size:0.9rem; color:#718096;">Steps Today</div>
                            <div style="font-size:2rem; font-weight:600; color:#4361EE;">{rt_data['steps']:,}</div>
                            <div style="font-size:0.9rem; color:#718096;">{int(rt_data['steps']/10000*100)}% of daily goal</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Stress level if available
                    if 'stress_level' in rt_data:
                        stress_color = "#48BB78" if rt_data['stress_level'] < 30 else "#F6AD55" if rt_data['stress_level'] < 70 else "#F56565"
                        st.markdown(f"""
                        <div style="background:white; border-radius:10px; padding:15px; margin-bottom:15px; box-shadow:0 2px 10px rgba(0,0,0,0.05);">
                            <div style="font-size:0.9rem; color:#718096;">Stress Level</div>
                            <div style="font-size:2rem; font-weight:600; color:{stress_color};">{rt_data['stress_level']}</div>
                            <div style="font-size:0.9rem; color:#718096;">{rt_data.get('stress_category', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Heart rate chart that updates in real-time
                if 'heart_rate' in rt_data:
                    # Store heart rate history in session state
                    if 'hr_history' not in st.session_state:
                        st.session_state.hr_history = []
                        st.session_state.hr_times = []
                    
                    # Add current data point
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    st.session_state.hr_history.append(rt_data['heart_rate'])
                    st.session_state.hr_times.append(current_time)
                    
                    # Keep only the last 20 data points
                    if len(st.session_state.hr_history) > 20:
                        st.session_state.hr_history = st.session_state.hr_history[-20:]
                        st.session_state.hr_times = st.session_state.hr_times[-20:]
                    
                    # Create chart
                    hr_chart_data = pd.DataFrame({
                        'Time': st.session_state.hr_times,
                        'Heart Rate': st.session_state.hr_history
                    })
                    
                    st.markdown("<h4 style='margin-top:20px;'>Heart Rate Monitoring</h4>", unsafe_allow_html=True)
                    st.line_chart(hr_chart_data.set_index('Time'))
                    
                    # Auto-refresh based on selected rate
                    refresh_seconds = {
                        "5 seconds": 5,
                        "10 seconds": 10,
                        "30 seconds": 30,
                        "1 minute": 60
                    }
                    
                    # Add auto-refresh
                    st.markdown(f"""
                    <div style="text-align:center; color:#718096; font-size:0.9rem; margin-top:10px;">
                        Auto-refreshing every {refresh_rate}. Last update: {current_time}
                    </div>
                    
                    <script>
                        setTimeout(function(){{
                            window.location.reload();
                        }}, {refresh_seconds[refresh_rate] * 1000});
                    </script>
                    """, unsafe_allow_html=True)
                
                # Display all available real-time data
                with st.expander("View All Real-Time Data", expanded=False):
                    st.json(rt_data)
            else:
                # Show placeholder when monitoring is not active
                st.markdown("""
                <div style="background:#F7FAFC; border-radius:10px; padding:30px; margin:20px 0; text-align:center;">
                    <div style="font-size:3rem; color:#A0AEC0; margin-bottom:20px;">⚡</div>
                    <div style="font-size:1.2rem; font-weight:600; color:#4A5568; margin-bottom:10px;">Real-Time Monitoring Not Active</div>
                    <div style="color:#718096; margin-bottom:20px;">Click "Start Monitoring" to begin tracking your health metrics in real-time.</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Tab 4: Settings
        with wearable_tabs[3]:
            st.markdown("<div style='background:#EDF2F7; border-radius:10px; padding:20px; margin-bottom:20px;'>", unsafe_allow_html=True)
            
            st.subheader("Privacy Settings")
            st.write("Control how your wearable data is processed:")
            
            privacy_col1, privacy_col2 = st.columns(2)
            
            with privacy_col1:
                st.checkbox("Process data locally only", value=True, 
                           help="When enabled, your raw data never leaves your device")
                st.checkbox("Encrypt stored data", value=True,
                           help="Adds an extra layer of protection to your stored data")
            
            with privacy_col2:
                st.checkbox("Share anonymized insights", value=False,
                           help="Contribute to research with fully anonymized data")
                st.checkbox("Delete old data automatically", value=False,
                           help="Automatically removes data older than 90 days")
            
            st.markdown("<div style='margin-top:15px;'>", unsafe_allow_html=True)
            st.write("NeuroSync prioritizes your privacy. Your raw health data is processed locally and never sent to external servers.")
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Device management
            st.markdown("<div style='background:#EDF2F7; border-radius:10px; padding:20px; margin-top:20px;'>", unsafe_allow_html=True)
            
            st.subheader("Device Management")
            st.write("Manage your connected devices and data sources:")
            
            # Connected devices (simulated)
            devices_col1, devices_col2 = st.columns([3, 1])
            
            with devices_col1:
                st.markdown("""
                <div style="margin:10px 0;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <strong>Apple Watch</strong><br>
                            <span style="color:#718096; font-size:0.9rem;">Last synced: Today at 10:30 AM</span>
                        </div>
                        <div>
                            <span style="color:#4361EE; cursor:pointer;">Disconnect</span>
                        </div>
                    </div>
                </div>
                <hr style="margin:15px 0; border-color:#E2E8F0;">
                <div style="margin:10px 0;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <strong>Apple HealthKit</strong><br>
                            <span style="color:#718096; font-size:0.9rem;">5 metrics connected</span>
                        </div>
                        <div>
                            <span style="color:#4361EE; cursor:pointer;">Configure</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with devices_col2:
                # Add device button
                st.markdown("<div style='margin-top:15px;'>", unsafe_allow_html=True)
                st.button("Add Device", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Data management
            st.subheader("Data Management")
            
            data_col1, data_col2 = st.columns(2)
            
            with data_col1:
                st.button("Export All Data", use_container_width=True)
            
            with data_col2:
                st.button("Clear All Data", use_container_width=True, type="primary")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Analysis & Insights page
    elif nav_option == "Analysis & Insights":
        st.title("Analysis & Insights")
        st.markdown("Discover patterns in your mental and physical health data")
        
        if not st.session_state.journal_entries or not st.session_state.wearable_data:
            st.warning("You need both journal entries and wearable data to generate insights. Please add more data.")
        else:
            # Perform analysis
            with st.spinner("Analyzing your data..."):
                # Decrypt journal entries for analysis
                decrypted_entries = [decrypt_data(entry) for entry in st.session_state.journal_entries]
                
                # Analyze mood patterns
                mood_insights = analyze_mood_patterns(decrypted_entries, st.session_state.wearable_data)
                
                # Predict stress levels
                stress_prediction = predict_stress_level(decrypted_entries[-1], st.session_state.wearable_data[-1])
            
            # Display insights
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Mood & Health Correlations")
                
                for insight in mood_insights:
                    st.info(insight)
                
                # Sample visualization
                st.subheader("Journal Mood vs. Sleep Quality")
                
                # Extract data
                dates = []
                mood_scores = []
                sleep_hours = []
                
                for entry in decrypted_entries:
                    entry_date = entry.get('date')
                    if entry_date:
                        dates.append(entry_date)
                        mood_scores.append(entry.get('mood_score', 0))
                        
                        # Find matching wearable data
                        matching_wearable = next(
                            (w for w in st.session_state.wearable_data if w.get('date') == entry_date), 
                            None
                        )
                        
                        if matching_wearable:
                            sleep_hours.append(matching_wearable.get('sleep_hours', 0))
                        else:
                            sleep_hours.append(0)
                
                # Create DataFrame for plotting
                correlation_df = pd.DataFrame({
                    'Date': dates,
                    'Mood Score': mood_scores,
                    'Sleep Hours': sleep_hours
                })
                
                # Plot
                st.line_chart(correlation_df.set_index('Date'))
                
            with col2:
                st.subheader("Stress Prediction")
                
                # Display stress prediction
                stress_level = stress_prediction.get('predicted_stress_level', 5)
                st.markdown(f"### Current Stress Level: {stress_level}/10")
                
                # Progress bar for visual representation
                st.progress(stress_level/10)
                
                # Interpretation
                if stress_level <= 3:
                    st.success("Your stress levels appear to be low right now.")
                elif stress_level <= 6:
                    st.warning("You're experiencing moderate stress levels.")
                else:
                    st.error("Your stress levels appear to be high. Consider using some coping strategies.")
                
                # Factors contributing to stress
                st.subheader("Contributing Factors")
                for factor, impact in stress_prediction.get('contributing_factors', {}).items():
                    st.write(f"**{factor}**: {impact}")
                
                # Personalized recommendations
                st.subheader("Recommendations")
                for recommendation in stress_prediction.get('recommendations', []):
                    st.info(recommendation)
    
    # Coping Strategies page
    elif nav_option == "Coping Strategies":
        st.title("Personalized Coping Strategies")
        st.markdown("AI-generated strategies based on your data to help manage stress and improve well-being")
        
        # Check if we have enough data to generate strategies
        if not st.session_state.journal_entries:
            st.warning("You need to add journal entries before getting personalized coping strategies.")
        else:
            # Form to request new strategies
            with st.form("generate_strategies"):
                st.subheader("Generate New Coping Strategies")
                
                # Specific focus areas
                focus_areas = st.multiselect(
                    "What areas would you like to focus on?",
                    ["Stress Reduction", "Sleep Improvement", "Mood Enhancement", 
                     "Anxiety Management", "Energy Levels", "Social Connection"]
                )
                
                # Time available
                time_available = st.slider(
                    "How much time do you have available (minutes)?",
                    5, 60, 15
                )
                
                # Environment
                environment = st.selectbox(
                    "Where will you be implementing these strategies?",
                    ["Home", "Work", "School", "Outdoors", "Public Place", "Other"]
                )
                
                # Submit button
                generate_submitted = st.form_submit_button("Generate Strategies")
                
                if generate_submitted:
                    if focus_areas:
                        with st.spinner("Generating personalized strategies..."):
                            # Get the most recent journal and wearable data
                            recent_journal = decrypt_data(st.session_state.journal_entries[-1]) if st.session_state.journal_entries else {}
                            recent_wearable = st.session_state.wearable_data[-1] if st.session_state.wearable_data else {}
                            
                            # Generate strategies using OpenAI
                            strategies = generate_coping_strategies(
                                recent_journal, 
                                recent_wearable,
                                focus_areas,
                                time_available,
                                environment
                            )
                            
                            # Add to session state with timestamp
                            strategy_entry = {
                                'date': datetime.datetime.now().strftime("%Y-%m-%d"),
                                'focus_areas': focus_areas,
                                'strategy': strategies
                            }
                            
                            st.session_state.coping_strategies.append(strategy_entry)
                            
                            # Save user data
                            user_data = {
                                'journal_entries': st.session_state.journal_entries,
                                'wearable_data': st.session_state.wearable_data,
                                'coping_strategies': st.session_state.coping_strategies
                            }
                            save_user_data(st.session_state.user_id, user_data)
                            
                            st.success("New coping strategies generated!")
                    else:
                        st.error("Please select at least one focus area")
            
            # Display saved strategies
            st.subheader("Your Coping Strategies")
            
            if st.session_state.coping_strategies:
                # Sort by date (newest first)
                sorted_strategies = sorted(
                    st.session_state.coping_strategies,
                    key=lambda x: datetime.datetime.strptime(x.get('date', '2000-01-01'), "%Y-%m-%d"),
                    reverse=True
                )
                
                for i, strategy in enumerate(sorted_strategies):
                    with st.expander(f"Strategy set from {strategy.get('date', 'No date')}"):
                        st.write(f"**Focus Areas:** {', '.join(strategy.get('focus_areas', ['General']))}")
                        st.write(strategy.get('strategy', 'No strategy available'))
                        
                        # Add a button to mark this strategy as helpful
                        if st.button(f"Mark as helpful", key=f"helpful_{i}"):
                            st.session_state.coping_strategies[i]['helpful'] = True
                            st.success("Thanks for your feedback! This helps improve future recommendations.")
            else:
                st.info("No coping strategies generated yet. Use the form above to create your first set.")
                
            # Provide some general coping strategies
            with st.expander("General Coping Strategies"):
                st.markdown("""
                ### Quick Stress Relief Techniques
                
                1. **Deep Breathing**: Take 5 slow, deep breaths, inhaling through your nose and exhaling through your mouth.
                
                2. **5-4-3-2-1 Grounding Exercise**: Name 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste.
                
                3. **Progressive Muscle Relaxation**: Tense and then release each muscle group in your body, starting from your toes and working upward.
                
                4. **Mindful Minute**: Take 60 seconds to focus entirely on your breathing, pulling your attention back when it wanders.
                
                5. **Quick Walk**: Take a 5-minute walk, preferably outdoors, focusing on the sensations and your surroundings.
                """)

# AI Coaching Page
    elif nav_option == "AI Coaching":
        # Custom page title with premium styling
        render_page_title(
            "AI Mental Health Coaching", 
            "Get personalized coaching from specialized AI models trained in mental health"
        )
        
        # Check for API key
        if not os.environ.get("OPENAI_API_KEY"):
            st.warning("⚠️ OpenAI API key is required for AI coaching features. Please contact the administrator to set up your API key.")
            
            # Show sample coaching interface without functionality
            st.markdown("### Sample Coaching Interface (API Key Required)")
            st.markdown("This is a preview of the AI coaching interface. Please configure your API key to access all features.")
            
            with st.expander("How AI Coaching Works"):
                st.markdown("""
                1. **Choose a Coaching Persona**: Select a specialized AI coach with expertise in specific mental health areas
                2. **Enter Your Coaching Request**: Describe your situation or question
                3. **Receive Personalized Guidance**: The AI coach will analyze your data and provide tailored advice
                4. **Track Your Progress**: Review your coaching history and monitor improvements
                """)
        else:
            # Initialize the chat interface if it doesn't exist
            if "active_coaching_session" not in st.session_state:
                st.session_state.active_coaching_session = False
                st.session_state.current_session_id = None
                st.session_state.current_persona = "general"
                st.session_state.session_messages = []
            
            # Create two columns for persona selection and coaching history
            persona_col, history_col = st.columns([3, 2])
            
            with persona_col:
                # Get available coaching personas
                coaching_personas = get_available_coaching_personas()
                
                # Display persona selection in a nice grid
                st.markdown("### Select a Specialized Mental Health Coach")
                
                # Convert personas to a 2-column grid
                persona_rows = [coaching_personas[i:i+2] for i in range(0, len(coaching_personas), 2)]
                
                # Generate a custom grid with cards
                html_content = """
                <div style="display:flex; flex-wrap:wrap; gap:10px; margin-bottom:20px;">
                """
                
                for persona in coaching_personas:
                    persona_id = persona["id"]
                    is_selected = persona_id == st.session_state.current_persona
                    border_style = "border:2px solid #4361EE;" if is_selected else "border:1px solid #E2E8F0;"
                    
                    html_content += f"""
                    <div onclick="selectPersona('{persona_id}')" style="cursor:pointer; flex:1; min-width:220px; background:#FFFFFF; 
                        {border_style} border-radius:10px; padding:15px; margin-bottom:10px; box-shadow:0 2px 5px rgba(0,0,0,0.05);">
                        <div style="font-weight:600; color:#2D3748; margin-bottom:5px;">{persona["name"]}</div>
                        <div style="font-size:0.9rem; color:#4A5568;">{persona["description"]}</div>
                    </div>
                    """
                
                html_content += """
                </div>
                <script>
                function selectPersona(id) {
                    // In a real app, we would use a callback. For now, we'll use URL parameters
                    window.location.href = "?persona=" + id;
                }
                </script>
                """
                
                st.markdown(html_content, unsafe_allow_html=True)
                
                # Fallback selection method (since the JS won't actually work in Streamlit)
                persona_id = st.selectbox(
                    "Select a coach:", 
                    options=[p["id"] for p in coaching_personas],
                    format_func=lambda id: next((p["name"] for p in coaching_personas if p["id"] == id), id),
                    index=[p["id"] for p in coaching_personas].index(st.session_state.current_persona)
                )
                
                # Update the current persona when changed
                if persona_id != st.session_state.current_persona:
                    st.session_state.current_persona = persona_id
            
            with history_col:
                st.markdown("### Your Coaching History")
                
                if st.session_state.coaching_history:
                    # Display coaching history with recent entries first
                    sorted_history = sorted(
                        st.session_state.coaching_history,
                        key=lambda x: x.get('date', ''),
                        reverse=True
                    )
                    
                    for entry in sorted_history[:5]:  # Show only the 5 most recent
                        entry_date = entry.get('date', 'No date')
                        focused_area = entry.get('focus', 'General wellbeing')
                        persona_used = entry.get('persona_name', 'Mental Health Coach')
                        
                        st.markdown(f"""
                        <div style="background:#EDF2F7; border-radius:8px; padding:12px; margin-bottom:10px;">
                            <div style="font-size:0.9rem; color:#4A5568;">{entry_date}</div>
                            <div style="font-weight:600; margin:4px 0;">{focused_area}</div>
                            <div style="font-size:0.85rem; color:#718096;">Coach: {persona_used}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if len(sorted_history) > 5:
                        st.markdown(f"*Plus {len(sorted_history) - 5} more sessions*")
                else:
                    st.markdown("""
                    <div style="background:#EDF2F7; border-radius:10px; padding:15px; text-align:center;">
                        <div style="color:#718096; margin-bottom:10px;">No coaching sessions yet</div>
                        <div style="font-size:0.9rem;">Your coaching history will appear here</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Coaching session interface
            st.markdown("### Get Personalized Mental Health Coaching")
            
            # Start a new coaching session if none active
            if not st.session_state.active_coaching_session:
                # Display form to start new session
                with st.form("start_coaching_session"):
                    # Get current persona details
                    current_persona = next(
                        (p for p in coaching_personas if p["id"] == st.session_state.current_persona), 
                        coaching_personas[0]
                    )
                    
                    st.markdown(f"""
                    <div style="margin-bottom:15px;">
                        <div style="font-weight:600; margin-bottom:5px;">Selected Coach: {current_persona["name"]}</div>
                        <div style="font-size:0.9rem; color:#4A5568;">{current_persona["description"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Coaching focus
                    coaching_focus = st.text_area(
                        "What would you like coaching on today?",
                        placeholder="Describe your situation or ask a specific question...",
                        height=100
                    )
                    
                    # Submit button
                    start_session = st.form_submit_button("Start Coaching Session")
                    
                    if start_session and coaching_focus:
                        # Create a session ID
                        session_id = f"session_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                        
                        # Initialize session messages
                        st.session_state.session_messages = []
                        
                        # Create user data from most recent entries
                        user_data = {}
                        
                        # Add journal data if available
                        if st.session_state.journal_entries:
                            recent_journal = decrypt_data(st.session_state.journal_entries[-1])
                            user_data['journal_data'] = recent_journal
                        
                        # Add wearable data if available
                        if st.session_state.wearable_data:
                            user_data['wearable_data'] = st.session_state.wearable_data[-1]
                        
                        try:
                            # Generate coaching advice
                            with st.spinner("Analyzing your data and generating personalized coaching..."):
                                coaching_response = generate_coaching_advice(
                                    user_data=user_data,
                                    coaching_focus=coaching_focus,
                                    persona_id=st.session_state.current_persona
                                )
                                
                                # Set active session
                                st.session_state.active_coaching_session = True
                                st.session_state.current_session_id = session_id
                                
                                # Store the initial exchange
                                st.session_state.session_messages = [
                                    {"role": "user", "content": coaching_focus},
                                    {"role": "assistant", "content": coaching_response}
                                ]
                                
                                # Add to coaching history
                                coaching_entry = {
                                    'date': datetime.datetime.now().strftime("%Y-%m-%d"),
                                    'session_id': session_id,
                                    'persona_id': st.session_state.current_persona,
                                    'persona_name': current_persona["name"],
                                    'focus': coaching_focus[:50] + "..." if len(coaching_focus) > 50 else coaching_focus,
                                    'messages': st.session_state.session_messages.copy()
                                }
                                
                                st.session_state.coaching_history.append(coaching_entry)
                                
                                # Save user data
                                user_data = {
                                    'journal_entries': st.session_state.journal_entries,
                                    'wearable_data': st.session_state.wearable_data,
                                    'coping_strategies': st.session_state.coping_strategies,
                                    'coaching_history': st.session_state.coaching_history
                                }
                                save_user_data(st.session_state.user_id, user_data)
                                
                                # Force a rerun to show the chat interface
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error generating coaching: {str(e)}")
                    elif start_session:
                        st.error("Please enter your coaching request before starting the session.")
            else:
                # Show active coaching session
                st.markdown("#### Active Coaching Session")
                
                # Display the chat history
                for msg in st.session_state.session_messages:
                    if msg["role"] == "user":
                        st.markdown(f"""
                        <div style="display:flex; margin-bottom:10px;">
                            <div style="background:#E2E8F0; border-radius:15px 15px 15px 0; padding:10px 15px; max-width:80%; margin-left:auto;">
                                <div style="font-size:0.9rem; color:#4A5568;">{msg["content"]}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="display:flex; margin-bottom:15px;">
                            <div style="background:#4361EE; color:white; border-radius:15px 15px 0 15px; padding:10px 15px; max-width:80%;">
                                <div style="font-size:0.9rem;">{msg["content"]}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Form for follow-up questions
                with st.form("coaching_follow_up"):
                    follow_up = st.text_area(
                        "Follow-up question",
                        placeholder="Ask a follow-up question or request further clarification...",
                        height=80
                    )
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        submit_follow_up = st.form_submit_button("Send")
                    with col2:
                        end_session = st.form_submit_button("End Session")
                    
                    if submit_follow_up and follow_up:
                        try:
                            # Get current persona and session details
                            current_persona = st.session_state.current_persona
                            session_history = st.session_state.session_messages.copy()
                            
                            # Add user message to history
                            session_history.append({"role": "user", "content": follow_up})
                            
                            # Create user data from most recent entries
                            user_data = {}
                            if st.session_state.journal_entries:
                                recent_journal = decrypt_data(st.session_state.journal_entries[-1])
                                user_data['journal_data'] = recent_journal
                            if st.session_state.wearable_data:
                                user_data['wearable_data'] = st.session_state.wearable_data[-1]
                            
                            # Generate follow-up response
                            with st.spinner("Generating response..."):
                                # Use coaching function with session history
                                coaching_response = generate_coaching_advice(
                                    user_data=user_data,
                                    coaching_focus=follow_up,
                                    persona_id=current_persona,
                                    session_history=session_history
                                )
                                
                                # Add response to history
                                session_history.append({"role": "assistant", "content": coaching_response})
                                st.session_state.session_messages = session_history
                                
                                # Update the coaching history
                                for entry in st.session_state.coaching_history:
                                    if entry.get('session_id') == st.session_state.current_session_id:
                                        entry['messages'] = session_history.copy()
                                        break
                                
                                # Save user data
                                user_data = {
                                    'journal_entries': st.session_state.journal_entries,
                                    'wearable_data': st.session_state.wearable_data,
                                    'coping_strategies': st.session_state.coping_strategies,
                                    'coaching_history': st.session_state.coaching_history
                                }
                                save_user_data(st.session_state.user_id, user_data)
                                
                                # Force a rerun to update the chat
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error generating response: {str(e)}")
                    elif submit_follow_up:
                        st.error("Please enter your follow-up question.")
                    
                    if end_session:
                        # End the current session
                        st.session_state.active_coaching_session = False
                        st.session_state.current_session_id = None
                        st.rerun()
            
            # Personalized exercise generator
            st.markdown("---")
            st.markdown("### Mental Health Exercise Generator")
            
            # Create a form for generating personalized exercises
            with st.form("generate_exercise"):
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    exercise_type = st.selectbox(
                        "Exercise type",
                        ["Meditation", "Breathing", "Gratitude", "Cognitive", "Physical", "Mindfulness"]
                    )
                
                with col2:
                    exercise_duration = st.slider(
                        "Duration (minutes)",
                        min_value=1,
                        max_value=30,
                        value=5,
                        step=1
                    )
                
                with col3:
                    difficulty = st.selectbox(
                        "Difficulty level",
                        ["beginner", "intermediate", "advanced"]
                    )
                
                generate_exercise = st.form_submit_button("Generate Exercise")
                
                if generate_exercise:
                    try:
                        # Create user data from most recent entries
                        user_data = {}
                        if st.session_state.journal_entries:
                            recent_journal = decrypt_data(st.session_state.journal_entries[-1])
                            user_data.update(recent_journal)
                        
                        # Generate personalized exercise
                        with st.spinner("Creating your personalized exercise..."):
                            exercise = generate_personalized_exercise(
                                user_data=user_data,
                                exercise_type=exercise_type,
                                duration_minutes=exercise_duration,
                                difficulty=difficulty
                            )
                            
                            # Display the generated exercise
                            st.subheader(exercise["title"])
                            st.markdown(exercise["introduction"])
                            
                            # Materials needed
                            if exercise["materials_needed"] and exercise["materials_needed"].lower() != "none needed":
                                st.markdown(f"**Materials needed:** {exercise['materials_needed']}")
                            
                            # Steps
                            st.markdown("#### Instructions")
                            if isinstance(exercise["steps"], list):
                                for i, step in enumerate(exercise["steps"], 1):
                                    st.markdown(f"{i}. {step}")
                            else:
                                st.markdown(exercise["steps"])
                            
                            # Tips and variations
                            if "tips" in exercise and exercise["tips"]:
                                st.markdown("#### Tips")
                                st.markdown(exercise["tips"])
                            
                            if "variations" in exercise and exercise["variations"]:
                                st.markdown("#### Variations")
                                st.markdown(exercise["variations"])
                            
                            if "daily_integration" in exercise and exercise["daily_integration"]:
                                st.markdown("#### Daily Integration")
                                st.markdown(exercise["daily_integration"])
                            
                    except Exception as e:
                        st.error(f"Error generating exercise: {str(e)}")

            # Progress analysis section
            if len(st.session_state.journal_entries) >= 2:
                st.markdown("---")
                st.markdown("### Your Mental Health Progress")
                
                # Analyze progress button
                if st.button("Analyze My Progress"):
                    try:
                        with st.spinner("Analyzing your mental health data..."):
                            # Get data for analysis
                            journal_entries = [decrypt_data(entry) for entry in st.session_state.journal_entries]
                            wearable_data = st.session_state.wearable_data
                            coaching_history = st.session_state.coaching_history
                            
                            # Analyze progress
                            progress = analyze_progress(
                                journal_entries=journal_entries,
                                wearable_data=wearable_data,
                                coaching_history=coaching_history,
                                timeframe_days=30
                            )
                            
                            if progress.get("sufficient_data", False):
                                # Display progress analysis
                                cols = st.columns(3)
                                
                                # Overall wellness score
                                with cols[0]:
                                    wellness_score = progress.get("wellness_score", 50)
                                    score_color = "#F56565" if wellness_score < 40 else "#4361EE" if wellness_score < 70 else "#48BB78"
                                    
                                    st.markdown(f"""
                                    <div style="background:linear-gradient(135deg, {score_color} 0%, #3A56D4 100%); 
                                        border-radius:10px; padding:20px; color:white; text-align:center;">
                                        <div style="font-size:0.9rem; opacity:0.8;">Wellness Score</div>
                                        <div style="font-size:2.5rem; font-weight:700; margin:5px 0;">{wellness_score}</div>
                                        <div style="font-size:0.9rem;">out of 100</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Overall trend
                                with cols[1]:
                                    trend = progress.get("overall_trend", "Insufficient data")
                                    st.markdown(f"""
                                    <div style="background:#EDF2F7; border-radius:10px; padding:20px; height:100%;">
                                        <div style="font-size:1rem; font-weight:600; color:#2D3748; margin-bottom:10px;">Overall Trend</div>
                                        <div style="font-size:0.95rem; color:#4A5568; line-height:1.5;">{trend}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Key improvements
                                with cols[2]:
                                    improvements = progress.get("key_improvements", ["No data available"])
                                    improvements_list = "".join([f"<li>{item}</li>" for item in improvements])
                                    
                                    st.markdown(f"""
                                    <div style="background:#EDF2F7; border-radius:10px; padding:20px; height:100%;">
                                        <div style="font-size:1rem; font-weight:600; color:#2D3748; margin-bottom:10px;">Key Improvements</div>
                                        <ul style="font-size:0.95rem; color:#4A5568; margin:0; padding-left:20px;">{improvements_list}</ul>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Challenge areas and recommendations
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    challenges = progress.get("challenge_areas", ["No data available"])
                                    challenges_list = "".join([f"<li>{item}</li>" for item in challenges])
                                    
                                    st.markdown(f"""
                                    <div style="background:#EDF2F7; border-radius:10px; padding:20px; margin-top:15px;">
                                        <div style="font-size:1rem; font-weight:600; color:#2D3748; margin-bottom:10px;">Areas for Growth</div>
                                        <ul style="font-size:0.95rem; color:#4A5568; margin:0; padding-left:20px;">{challenges_list}</ul>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                with col2:
                                    recommendations = progress.get("recommendations", ["No recommendations available"])
                                    recommendations_list = "".join([f"<li>{item}</li>" for item in recommendations])
                                    
                                    st.markdown(f"""
                                    <div style="background:#EDF2F7; border-radius:10px; padding:20px; margin-top:15px;">
                                        <div style="font-size:1rem; font-weight:600; color:#2D3748; margin-bottom:10px;">Recommendations</div>
                                        <ul style="font-size:0.95rem; color:#4A5568; margin:0; padding-left:20px;">{recommendations_list}</ul>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Correlations
                                if "correlations" in progress and progress["correlations"]:
                                    st.markdown(f"""
                                    <div style="background:#EDF2F7; border-radius:10px; padding:20px; margin-top:15px;">
                                        <div style="font-size:1rem; font-weight:600; color:#2D3748; margin-bottom:10px;">Key Correlations</div>
                                        <div style="font-size:0.95rem; color:#4A5568; line-height:1.5;">{progress["correlations"]}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info(progress.get("message", "Insufficient data to analyze progress. Please continue using the app regularly."))
                    except Exception as e:
                        st.error(f"Error analyzing progress: {str(e)}")
    
    # Zen Garden Page
    elif nav_option == "Zen Garden":
        # Custom page title with premium styling
        render_page_title(
            "Zen Garden Meditation", 
            "Create your personal meditation space for mindfulness practice"
        )
        
        # Initialize zen garden data if not exists
        if 'zen_garden_data' not in st.session_state:
            st.session_state.zen_garden_data = create_default_garden()
            
        # Two-column layout
        zen_col1, zen_col2 = st.columns([3, 1])
        
        with zen_col1:
            # Display Zen Garden
            garden_tabs = st.tabs(["View Garden", "Edit Garden"])
            
            with garden_tabs[0]: # View mode
                # Display the garden in view mode
                st.markdown(get_zen_garden_html(
                    garden_data=st.session_state.zen_garden_data,
                    mode="view"
                ), unsafe_allow_html=True)
                
                # Add meditation timer controls
                st.markdown("<h3 style='color:#4361EE; font-size:1.3rem; margin-top:20px;'>Guided Meditation</h3>", unsafe_allow_html=True)
                
                meditation_col1, meditation_col2, meditation_col3 = st.columns(3)
                with meditation_col1:
                    meditation_duration = st.selectbox("Duration", [
                        "5 minutes", "10 minutes", "15 minutes", "20 minutes"
                    ], key="meditation_duration")
                with meditation_col2:
                    meditation_focus = st.selectbox("Focus Area", [
                        "Breath", "Body", "Compassion"
                    ], key="meditation_focus")
                with meditation_col3:
                    if st.button("Start Guided Meditation"):
                        duration_minutes = int(meditation_duration.split()[0])
                        meditation_text = get_guided_meditation_text(
                            duration_minutes=duration_minutes,
                            focus=meditation_focus.lower()
                        )
                        
                        # Store this as a session
                        st.session_state.zen_garden_data = record_meditation_session(
                            garden_data=st.session_state.zen_garden_data,
                            duration_minutes=duration_minutes
                        )
                        
                        # Save user data
                        user_data = {
                            'journal_entries': st.session_state.journal_entries,
                            'wearable_data': st.session_state.wearable_data,
                            'coping_strategies': st.session_state.coping_strategies,
                            'coaching_history': st.session_state.coaching_history,
                            'zen_garden_data': st.session_state.zen_garden_data
                        }
                        save_user_data(st.session_state.user_id, user_data)
                
                # Display a zen wisdom quote
                st.markdown(f"""
                <div style="background:#EDF2F7; border-radius:10px; padding:20px; margin-top:20px; text-align:center;">
                    <div style="font-size:1.8rem; color:#A0AEC0; margin-bottom:15px;">☯</div>
                    <div style="font-style:italic; color:#4A5568; font-size:1.1rem; margin-bottom:5px;">"{generate_zen_wisdom()}"</div>
                </div>
                """, unsafe_allow_html=True)
                
            with garden_tabs[1]: # Edit mode
                # Display the garden in edit mode
                st.markdown(get_zen_garden_html(
                    garden_data=st.session_state.zen_garden_data,
                    mode="edit"
                ), unsafe_allow_html=True)
                
                # Add save button
                if st.button("Save Garden Changes"):
                    # In a real application, we would get data from the frontend
                    # For demo, we'll just save the current state
                    st.session_state.zen_garden_data["last_modified"] = datetime.datetime.now().strftime("%Y-%m-%d")
                    
                    # Save user data
                    user_data = {
                        'journal_entries': st.session_state.journal_entries,
                        'wearable_data': st.session_state.wearable_data,
                        'coping_strategies': st.session_state.coping_strategies,
                        'coaching_history': st.session_state.coaching_history,
                        'zen_garden_data': st.session_state.zen_garden_data
                    }
                    save_user_data(st.session_state.user_id, user_data)
                    
                    st.success("Your Zen Garden has been saved!")
        
        with zen_col2:
            # Meditation statistics
            st.markdown("<h3 style='color:#4361EE; font-size:1.2rem;'>Meditation Stats</h3>", unsafe_allow_html=True)
            
            # Calculate stats
            meditation_stats = get_meditation_stats(st.session_state.zen_garden_data)
            
            # Display stats card
            st.markdown(f"""
            <div style="background:#EDF2F7; border-radius:10px; padding:15px; margin-bottom:15px;">
                <div style="margin-bottom:15px;">
                    <div style="font-size:0.9rem; color:#4A5568; margin-bottom:5px;">Total Sessions</div>
                    <div style="font-size:1.8rem; font-weight:700; color:#4361EE;">{meditation_stats.get('total_sessions', 0)}</div>
                </div>
                
                <div style="margin-bottom:15px;">
                    <div style="font-size:0.9rem; color:#4A5568; margin-bottom:5px;">Meditation Minutes</div>
                    <div style="font-size:1.8rem; font-weight:700; color:#4361EE;">{meditation_stats.get('total_minutes', 0)}</div>
                </div>
                
                <div style="margin-bottom:15px;">
                    <div style="font-size:0.9rem; color:#4A5568; margin-bottom:5px;">Current Streak</div>
                    <div style="font-size:1.8rem; font-weight:700; color:#4361EE;">{meditation_stats.get('streak_days', 0)} days</div>
                </div>
                
                <div style="margin-bottom:0px;">
                    <div style="font-size:0.9rem; color:#4A5568; margin-bottom:5px;">Longest Session</div>
                    <div style="font-size:1.8rem; font-weight:700; color:#4361EE;">{meditation_stats.get('longest_session', 0)} min</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Benefits of meditation
            st.markdown("<h3 style='color:#4361EE; font-size:1.2rem; margin-top:20px;'>Benefits of Meditation</h3>", unsafe_allow_html=True)
            
            meditation_benefits = [
                {"title": "Reduces Stress", "icon": "🧘", "description": "Regular meditation decreases the production of stress hormones like cortisol."},
                {"title": "Improves Focus", "icon": "🎯", "description": "Meditation enhances attention span and concentration abilities."},
                {"title": "Better Sleep", "icon": "😴", "description": "People who meditate regularly often experience improved sleep quality."},
                {"title": "Emotional Balance", "icon": "⚖️", "description": "Meditation helps regulate emotions and reduce reactive responses."}
            ]
            
            for benefit in meditation_benefits:
                st.markdown(f"""
                <div style="background:#EDF2F7; border-radius:10px; padding:12px; margin-bottom:10px;">
                    <div style="display:flex; align-items:center; margin-bottom:5px;">
                        <span style="font-size:1.2rem; margin-right:8px;">{benefit['icon']}</span>
                        <div style="font-weight:600; color:#2D3748;">{benefit['title']}</div>
                    </div>
                    <div style="font-size:0.9rem; color:#4A5568;">{benefit['description']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Resources section
            st.markdown("<h3 style='color:#4361EE; font-size:1.2rem; margin-top:20px;'>Meditation Resources</h3>", unsafe_allow_html=True)
            
            st.markdown("""
            <div style="background:#EDF2F7; border-radius:10px; padding:15px; margin-bottom:15px;">
                <div style="font-weight:600; color:#2D3748; margin-bottom:10px;">Recommended Reading</div>
                <ul style="margin:0; padding-left:20px; color:#4A5568;">
                    <li>"The Miracle of Mindfulness" by Thich Nhat Hanh</li>
                    <li>"Wherever You Go, There You Are" by Jon Kabat-Zinn</li>
                    <li>"Why Buddhism is True" by Robert Wright</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("NeuroSync - Your Privacy-First Mental Health Companion")
st.markdown("All data is processed locally for maximum privacy protection")
