import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime

def plot_mood_trend(dates, mood_scores):
    """
    Plot mood trends over time.
    
    Args:
        dates: List of date strings
        mood_scores: List of mood scores (1-10)
    """
    if not dates or not mood_scores or len(dates) != len(mood_scores):
        st.warning("Insufficient data to plot mood trend")
        return
    
    # Convert to DataFrame for easier plotting
    df = pd.DataFrame({
        'Date': dates,
        'Mood': mood_scores
    })
    
    # Sort by date
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    # Plot using Streamlit
    st.line_chart(df.set_index('Date'))

def plot_sleep_heart_correlation(dates, sleep_data, heart_data):
    """
    Plot sleep and heart rate data over time.
    
    Args:
        dates: List of date strings
        sleep_data: List of sleep hours
        heart_data: List of heart rate values
    """
    if not dates or not sleep_data or not heart_data:
        st.warning("Insufficient data to plot sleep and heart rate correlation")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Sleep Hours': sleep_data,
        'Heart Rate': heart_data
    })
    
    # Sort by date
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    # Create two y-axes chart using Streamlit
    # First, plot sleep hours
    st.line_chart(df[['Date', 'Sleep Hours']].set_index('Date'))
    
    # Then, plot heart rate
    st.line_chart(df[['Date', 'Heart Rate']].set_index('Date'))
    
    # Calculate correlation
    correlation = df['Sleep Hours'].corr(df['Heart Rate'])
    
    # Display correlation
    st.write(f"Correlation coefficient between sleep and heart rate: {correlation:.2f}")
    
    if correlation < -0.5:
        st.info("Your heart rate tends to be lower when you get more sleep, which is a healthy pattern.")
    elif correlation > 0.5:
        st.warning("Interestingly, your heart rate tends to be higher when you get more sleep. This might be worth discussing with a healthcare provider.")

def plot_stress_factors(stress_data):
    """
    Create a radar chart of factors contributing to stress.
    
    Args:
        stress_data: Dictionary with stress factors and their values
    """
    if not stress_data:
        st.warning("Insufficient data to plot stress factors")
        return
    
    # Convert the data to lists for plotting
    categories = list(stress_data.keys())
    values = list(stress_data.values())
    
    # Use matplotlib to create the radar chart
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, polar=True)
    
    # Compute angle for each category
    angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
    
    # Make the plot circular
    values.append(values[0])
    angles.append(angles[0])
    categories.append(categories[0])
    
    # Plot data
    ax.plot(angles, values, 'o-', linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    
    # Set category labels
    ax.set_thetagrids(np.degrees(angles[:-1]), categories[:-1])
    
    # Set chart title
    ax.set_title("Stress Contributing Factors")
    
    # Display in Streamlit
    st.pyplot(fig)

def plot_weekly_summary(journal_entries, wearable_data):
    """
    Create a weekly summary visualization.
    
    Args:
        journal_entries: List of journal entry dictionaries
        wearable_data: List of wearable data dictionaries
    """
    if not journal_entries or not wearable_data:
        st.warning("Insufficient data for weekly summary")
        return
    
    # Get last 7 days of data
    today = datetime.now().date()
    
    # Extract mood data from journal entries
    mood_by_day = {}
    stress_by_day = {}
    
    for entry in journal_entries:
        entry_date = entry.get('date')
        if entry_date:
            try:
                date_obj = datetime.strptime(entry_date, "%Y-%m-%d").date()
                day_name = date_obj.strftime("%a")
                mood_by_day[day_name] = entry.get('mood_score', 0)
                stress_by_day[day_name] = entry.get('stress_level', 0)
            except ValueError:
                continue
    
    # Extract sleep and activity data from wearable
    sleep_by_day = {}
    steps_by_day = {}
    
    for data in wearable_data:
        data_date = data.get('date')
        if data_date:
            try:
                date_obj = datetime.strptime(data_date, "%Y-%m-%d").date()
                day_name = date_obj.strftime("%a")
                sleep_by_day[day_name] = data.get('sleep_hours', 0)
                steps_by_day[day_name] = data.get('steps', 0)
            except ValueError:
                continue
    
    # Create a DataFrame for the weekly summary
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    summary_data = {
        'Day': days,
        'Mood': [mood_by_day.get(day, None) for day in days],
        'Stress': [stress_by_day.get(day, None) for day in days],
        'Sleep': [sleep_by_day.get(day, None) for day in days],
        'Steps': [steps_by_day.get(day, None) for day in days]
    }
    
    df = pd.DataFrame(summary_data)
    
    # Replace None with NaN for plotting
    df = df.replace({None: np.nan})
    
    # Display the weekly summary
    st.subheader("Weekly Summary")
    
    # Display mood trend
    st.write("Mood Trend")
    st.line_chart(df[['Day', 'Mood']].set_index('Day'))
    
    # Display stress trend
    st.write("Stress Trend")
    st.line_chart(df[['Day', 'Stress']].set_index('Day'))
    
    # Display sleep trend
    st.write("Sleep Hours")
    st.bar_chart(df[['Day', 'Sleep']].set_index('Day'))
    
    # Display steps trend
    st.write("Daily Steps")
    st.bar_chart(df[['Day', 'Steps']].set_index('Day'))
