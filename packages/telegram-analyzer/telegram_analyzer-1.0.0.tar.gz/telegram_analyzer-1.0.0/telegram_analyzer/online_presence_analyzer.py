"""
Online Presence Analyzer Module for Telegram Analyzer.
This module analyzes user online presence patterns and behaviors.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter

class OnlinePresenceAnalyzer:
    """Analyzer for user online presence, activity patterns, and interaction behaviors"""
    
    def __init__(self, messages_df: pd.DataFrame, output_dir: str):
        """
        Initialize the online presence analyzer.
        
        Args:
            messages_df: DataFrame containing message data with 'from' and 'date' columns
            output_dir: Directory to save output files and visualizations
        """
        self.logger = logging.getLogger(__name__)
        self.messages_df = messages_df.copy()
        self.output_dir = output_dir
        
        # Validate required columns
        required_columns = ['from', 'date']
        for column in required_columns:
            if column not in self.messages_df.columns:
                self.logger.error(f"Required column '{column}' not found in messages DataFrame")
                raise ValueError(f"Required column '{column}' not found in messages DataFrame")
        
        # Ensure date column is datetime type
        if not pd.api.types.is_datetime64_any_dtype(self.messages_df['date']):
            self.logger.warning("Converting 'date' column to datetime")
            self.messages_df['date'] = pd.to_datetime(self.messages_df['date'])
        
        # Filter out any rows with None in the 'from' column
        self.messages_df = self.messages_df[self.messages_df['from'].notna()].reset_index(drop=True)
        
        # Extract key time features
        self.messages_df['hour'] = self.messages_df['date'].dt.hour
        self.messages_df['day_of_week'] = self.messages_df['date'].dt.day_name()
        self.messages_df['day'] = self.messages_df['date'].dt.date
        
        # Define time periods for analysis
        self.time_periods = {
            'morning': (5, 11),    # 5 AM - 11:59 AM
            'afternoon': (12, 16), # 12 PM - 4:59 PM
            'evening': (17, 21),   # 5 PM - 9:59 PM
            'night': (22, 4)       # 10 PM - 4:59 AM
        }
        
        # Create time period column
        self.messages_df['time_period'] = self.messages_df['hour'].apply(self._get_time_period)
        
        # Create previous and next message columns for response analysis
        self._prepare_conversation_data()

    def _get_time_period(self, hour: int) -> str:
        """
        Determine time period (morning, afternoon, evening, night) for a given hour.
        
        Args:
            hour: Hour of day (0-23)
            
        Returns:
            String representing the time period
        """
        if 5 <= hour <= 11:
            return 'morning'
        elif 12 <= hour <= 16:
            return 'afternoon'
        elif 17 <= hour <= 21:
            return 'evening'
        else:  # 22-23, 0-4
            return 'night'
    
    def _prepare_conversation_data(self):
        """Prepare data for conversation and response analysis"""
        # Sort by date
        sorted_df = self.messages_df.sort_values('date').reset_index(drop=True)
        
        # Create columns for previous and next message info
        sorted_df['prev_message_time'] = sorted_df['date'].shift(1)
        sorted_df['prev_message_user'] = sorted_df['from'].shift(1)
        sorted_df['next_message_time'] = sorted_df['date'].shift(-1)
        sorted_df['next_message_user'] = sorted_df['from'].shift(-1)
        
        # Calculate time between messages
        sorted_df['time_since_prev'] = (sorted_df['date'] - sorted_df['prev_message_time']).dt.total_seconds() / 60
        sorted_df['time_until_next'] = (sorted_df['next_message_time'] - sorted_df['date']).dt.total_seconds() / 60
        
        # Flag if message is a response (different user from previous message)
        sorted_df['is_response'] = sorted_df['from'] != sorted_df['prev_message_user']
        
        # Flag if message received a response (different user for next message)
        sorted_df['got_response'] = sorted_df['from'] != sorted_df['next_message_user']
        
        # Flag quick responses (within 5 minutes)
        sorted_df['quick_response'] = (sorted_df['is_response'] & (sorted_df['time_since_prev'] <= 5))
        
        # Update our main dataframe
        self.messages_df = sorted_df
    
    def get_online_time_stats(self) -> Dict:
        """
        Get comprehensive online time statistics for users.
        
        Returns:
            Dictionary containing various online time and presence statistics
        """
        stats = {}
        
        # Calculate active days per user
        user_active_days = {}
        for user in self.messages_df['from'].unique():
            user_days = self.messages_df[self.messages_df['from'] == user]['day'].nunique()
            user_active_days[user] = user_days
        
        # Most and least active users by days
        most_active_user = max(user_active_days.items(), key=lambda x: x[1])
        least_active_user = min(user_active_days.items(), key=lambda x: x[1])
        
        stats['most_active_user_days'] = {
            'user': most_active_user[0],
            'active_days': most_active_user[1]
        }
        
        stats['least_active_user_days'] = {
            'user': least_active_user[0],
            'active_days': least_active_user[1]
        }
        
        # Daily activity patterns
        day_counts = self.messages_df['day_of_week'].value_counts()
        most_active_day = day_counts.idxmax()
        least_active_day = day_counts.idxmin()
        
        stats['most_active_day'] = most_active_day
        stats['least_active_day'] = least_active_day
        
        # Time period preference by user
        user_time_periods = {}
        for user in self.messages_df['from'].unique():
            user_data = self.messages_df[self.messages_df['from'] == user]
            period_counts = user_data['time_period'].value_counts()
            preferred_period = period_counts.idxmax() if not period_counts.empty else None
            user_time_periods[user] = preferred_period
        
        stats['user_preferred_periods'] = user_time_periods
        
        # Identify early birds (most active in the morning)
        morning_users = self.messages_df[self.messages_df['time_period'] == 'morning']['from'].value_counts()
        early_birds = morning_users.nlargest(3).index.tolist()
        stats['early_birds'] = early_birds
        
        # Identify night owls (most active at night)
        night_users = self.messages_df[self.messages_df['time_period'] == 'night']['from'].value_counts()
        night_owls = night_users.nlargest(3).index.tolist()
        stats['night_owls'] = night_owls
        
        # Response patterns
        response_stats = self._get_response_stats()
        stats.update(response_stats)
        
        # Consistency analysis
        consistency_stats = self._get_consistency_stats()
        stats.update(consistency_stats)
        
        # Absence detection
        absence_stats = self._detect_user_absences()
        stats.update(absence_stats)
        
        # Calculate online presence without responses
        ghoster_stats = self._identify_ghosters()
        stats.update(ghoster_stats)
        
        return stats
        
    def generate_online_presence_report(self) -> str:
        """
        Generate a detailed HTML report of online presence statistics.
        
        Returns:
            Path to the generated HTML report
        """
        try:
            stats = self.get_online_time_stats()
            
            # Generate visualizations
            viz_files = self.generate_online_presence_visualizations()
            
            # Create HTML report
            html_content = self._create_html_report(stats, viz_files)
            
            # Save report
            report_path = os.path.join(self.output_dir, 'online_presence_report.html')
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            self.logger.info(f"Online presence report generated at {report_path}")
            return report_path
            
        except Exception as e:
            self.logger.error(f"Error generating online presence report: {str(e)}")
            return ""
    
    def _create_html_report(self, stats: Dict, viz_files: List[str]) -> str:
        """Create HTML content for the online presence report"""
        
        # Format time periods for display
        time_period_labels = {
            'morning': 'Morning (5 AM - 12 PM)',
            'afternoon': 'Afternoon (12 PM - 5 PM)',
            'evening': 'Evening (5 PM - 10 PM)',
            'night': 'Night (10 PM - 5 AM)'
        }
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Telegram Chat Online Presence Analysis</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    margin: 0;
                    padding: 0;
                    color: #333;
                    background-color: #f8f9fa;
                }}
                .container {{ padding: 2rem; }}
                .card {{ 
                    margin-bottom: 1.5rem; 
                    border-radius: 8px; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .card-header {{ 
                    font-weight: bold; 
                    background-color: #f8f9fa;
                    border-bottom: 1px solid #e9ecef;
                }}
                .viz-img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                    margin: 1rem 0;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }}
                .stat-value {{
                    font-size: 1.2rem;
                    font-weight: bold;
                    color: #0d6efd;
                }}
                .info-block {{
                    margin-bottom: 1rem;
                    padding: 0.5rem;
                    border-radius: 6px;
                    background-color: #e9ecef;
                }}
                .user-list {{
                    list-style-type: none;
                    padding-left: 0;
                }}
                .user-list li {{
                    padding: 0.5rem;
                    margin: 0.25rem 0;
                    background-color: #f1f3f5;
                    border-radius: 4px;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 1rem;
                }}
                .navbar {{
                    background-color: #0d6efd;
                    color: white;
                    padding: 1rem;
                    margin-bottom: 2rem;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    color: #0d6efd;
                }}
                .back-link {{
                    color: white;
                    margin-right: 1rem;
                    text-decoration: none;
                    display: inline-block;
                }}
                .back-link:hover {{
                    text-decoration: underline;
                    color: #f0f0f0;
                }}
            </style>
            </head>
            <body>
                <div class="navbar">
                    <div class="container">
                        <a href="report.html" class="back-link"><i class="fas fa-arrow-left"></i> Back to Main Report</a>
                        <h1><i class="fab fa-telegram"></i> Telegram Chat Online Presence Analysis</h1>
                    </div>
                </div>
                
                <div class="container">
                    <div class="row">
                        <div class="col-12">
                        <div class="card">
                            <div class="card-header">
                                <h2><i class="fas fa-chart-line"></i> User Activity Overview</h2>
                            </div>
                            <div class="card-body">
                                <div class="stats-grid">
    """
        
        # Add active user stats
        if 'most_active_user_days' in stats:
            html += f"""
                                    <div class="info-block">
                                        <h5>Most Active User (by Days)</h5>
                                        <p class="stat-value">{stats['most_active_user_days']['user']}</p>
                                        <p>Active for {stats['most_active_user_days']['active_days']} days</p>
                                    </div>
            """
            
        if 'least_active_user_days' in stats:
            html += f"""
                                    <div class="info-block">
                                        <h5>Least Active User (by Days)</h5>
                                        <p class="stat-value">{stats['least_active_user_days']['user']}</p>
                                        <p>Active for only {stats['least_active_user_days']['active_days']} days</p>
                                    </div>
            """
            
        # Add day activity stats
        if 'most_active_day' in stats and 'least_active_day' in stats:
            html += f"""
                                    <div class="info-block">
                                        <h5>Most Active Day</h5>
                                        <p class="stat-value">{stats['most_active_day']}</p>
                                    </div>
                                    
                                    <div class="info-block">
                                        <h5>Least Active Day</h5>
                                        <p class="stat-value">{stats['least_active_day']}</p>
                                    </div>
            """
        
        # Close stats grid
        html += """
                                </div>
                                
                                <div class="row mt-4">
                                    <div class="col-12">
                                        <h4>Daily and Hourly Activity Patterns</h4>
        """
        
        # Add activity heatmap
        if 'user_activity_heatmap.png' in viz_files:
            html += """
                                        <img src="user_activity_heatmap.png" class="viz-img" alt="User Activity Heatmap">
                                        <p class="text-muted">This heatmap shows when users are most active throughout the week.</p>
            """
            # Add activity heatmap
        if 'user_message_timeline.png' in viz_files:
            html += """
                                        <img src="user_message_timeline.png" class="viz-img" alt="User Activity Heatmap">
                                        <p class="text-muted">This heatmap shows when users are most active throughout the week.</p>
            """
            # Close activity patterns section
        html += """
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="card">
                            <div class="card-header">
                                <h2><i class="fas fa-clock"></i> Time Preferences</h2>
                            </div>
                            <div class="card-body">
        """
        
        # Add early birds and night owls
        if 'early_birds' in stats:
            html += """
                                <div class="row">
                                    <div class="col-md-6">
                                        <h4>Early Birds (Morning People)</h4>
                                        <ul class="user-list">
            """
            
            for user in stats['early_birds']:
                html += f"""
                                            <li><i class="fas fa-sun"></i> {user}</li>
                """
                
            html += """
                                        </ul>
                                    </div>
            """
        
        if 'night_owls' in stats:
            html += """
                                    <div class="col-md-6">
                                        <h4>Night Owls</h4>
                                        <ul class="user-list">
            """
            
            for user in stats['night_owls']:
                html += f"""
                                            <li><i class="fas fa-moon"></i> {user}</li>
                """
                
            html += """
                                        </ul>
                                    </div>
                                </div>
            """
        
        # Add user preferred periods
        if 'user_preferred_periods' in stats:
            html += """
                                <div class="row mt-4">
                                    <div class="col-12">
                                        <h4>User Time Period Preferences</h4>
                                        <div class="row">
            """
            
            for period in ['morning', 'afternoon', 'evening', 'night']:
                users = [user for user, pref in stats['user_preferred_periods'].items() if pref == period]
                if users:
                    html += f"""
                                            <div class="col-md-3">
                                                <h5>{time_period_labels.get(period, period.title())}</h5>
                                                <ul class="user-list">
                    """
                    
                    for user in users[:5]:  # Show top 5 for each period
                        html += f"""
                                                    <li>{user}</li>
                        """
                        
                    if len(users) > 5:
                        html += f"""
                                                    <li>+{len(users) - 5} more</li>
                        """
                        
                    html += """
                                                </ul>
                                            </div>
                    """
            
            html += """
                                        </div>
                                    </div>
                                </div>
            """
        
        # Add time preferences chart
        if 'user_time_preferences.png' in viz_files:
            html += """
                                <div class="row mt-4">
                                    <div class="col-12">
                                        <img src="user_time_preferences.png" class="viz-img" alt="User Time Preferences">
                                        <p class="text-muted">This chart shows when each user is most active during the day.</p>
                                    </div>
                                </div>
            """
        
        # Close time preferences card
        html += """
                            </div>
                        </div>
                        
                        <div class="card">
                            <div class="card-header">
                                <h2><i class="fas fa-reply"></i> Response Patterns</h2>
                            </div>
                            <div class="card-body">
                                <div class="stats-grid">
        """
        
        # Add response stats
        response_stats = [
            ('fastest_responder', 'Fastest Responder', lambda s: f"{s['user']} ({s['avg_time_minutes']:.1f} min)"),
            ('slowest_responder', 'Slowest Responder', lambda s: f"{s['user']} ({s['avg_time_minutes']:.1f} min)"),
            ('most_responsive_user', 'Most Responsive User', lambda s: f"{s['user']} ({s['response_rate'] * 100:.1f}%)"),
            ('least_responsive_user', 'Least Responsive User', lambda s: f"{s['user']} ({s['response_rate'] * 100:.1f}%)"),
            ('most_ignored_user', 'Most Ignored User', lambda s: f"{s['user']} ({s['got_response_rate'] * 100:.1f}%)"),
            ('most_engaging_user', 'Most Engaging User', lambda s: f"{s['user']} ({s['got_response_rate'] * 100:.1f}%)")
        ]
        
        for key, title, formatter in response_stats:
            if key in stats:
                html += f"""
                                    <div class="info-block">
                                        <h5>{title}</h5>
                                        <p class="stat-value">{formatter(stats[key])}</p>
                                    </div>
                """
        
        # Close stats grid
        html += """
                                </div>
                                
                                <div class="row mt-4">
                                    <div class="col-md-6">
        """
        
        # Add response time chart
        if 'response_time_distribution.png' in viz_files:
            html += """
                                        <h4>Response Time Distribution</h4>
                                        <img src="response_time_distribution.png" class="viz-img" alt="Response Time Distribution">
                                        <p class="text-muted">This chart shows how quickly users respond to messages.</p>
            """
            
        html += """
                                    </div>
                                    <div class="col-md-6">
        """
        
        # Add response network
        if 'user_response_network.png' in viz_files:
            html += """
                                        <h4>User Response Network</h4>
                                        <img src="user_response_network.png" class="viz-img" alt="User Response Network">
                                        <p class="text-muted">This network shows who responds to whom in the chat.</p>
            """
            
        html += """
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="card">
                            <div class="card-header">
                                <h2><i class="fas fa-ghost"></i> "Ghosting" Analysis</h2>
                            </div>
                            <div class="card-body">
                                <p>
                                    This analysis identifies users who are present in the chat but tend not to respond to others.
                                    A high "ghosting" score means a user reads messages but rarely responds.
                                </p>
        """
        
        # Add ghosting stats
        if 'top_ghosters' in stats:
            html += """
                                <div class="row">
                                    <div class="col-md-6">
                                        <h4>Top "Ghosters"</h4>
                                        <ul class="user-list">
            """
            
            for user in stats['top_ghosters']:
                html += f"""
                                            <li><i class="fas fa-ghost"></i> {user}</li>
                """
                
            html += """
                                        </ul>
                                    </div>
            """
            
        if 'most_engaged_users' in stats:
            html += """
                                    <div class="col-md-6">
                                        <h4>Most Engaged Users</h4>
                                        <ul class="user-list">
            """
            
            for user in stats['most_engaged_users']:
                html += f"""
                                            <li><i class="fas fa-comments"></i> {user}</li>
                """
                
            html += """
                                        </ul>
                                    </div>
                                </div>
            """
        
        # Add ghosting chart
        if 'user_ghosting_scores.png' in viz_files:
            html += """
                                <div class="row mt-4">
                                    <div class="col-12">
                                        <img src="user_ghosting_scores.png" class="viz-img" alt="User Ghosting Scores">
                                        <p class="text-muted">This chart shows users ranked by their tendency to "ghost" (be present but not respond).</p>
                                    </div>
                                </div>
            """
        
        # Close ghosting card
        html += """
                            </div>
                        </div>
                        
                        <div class="card">
                            <div class="card-header">
                                <h2><i class="fas fa-calendar-check"></i> Consistency Analysis</h2>
                            </div>
                            <div class="card-body">
                                <div class="stats-grid">
        """
        
        # Add consistency stats
        consistency_stats = [
            ('most_consistent_user', 'Most Consistent User', lambda s: f"{s['user']} ({s['consistency_score'] * 100:.1f}%)"),
            ('least_consistent_user', 'Least Consistent User', lambda s: f"{s['user']} ({s['consistency_score'] * 100:.1f}%)"),
            ('most_time_consistent_user', 'Most Consistent Time', lambda s: f"{s['user']} (var: {s['hour_variance']:.2f})"),
            ('least_time_consistent_user', 'Least Consistent Time', lambda s: f"{s['user']} (var: {s['hour_variance']:.2f})")
        ]
        
        for key, title, formatter in consistency_stats:
            if key in stats:
                html += f"""
                                    <div class="info-block">
                                        <h5>{title}</h5>
                                        <p class="stat-value">{formatter(stats[key])}</p>
                                    </div>
                """
        
        # Close stats grid
        html += """
                                </div>
        """
        
        # Add consistency chart
        if 'user_consistency_scores.png' in viz_files:
            html += """
                                <div class="row mt-4">
                                    <div class="col-12">
                                        <img src="user_consistency_scores.png" class="viz-img" alt="User Consistency Scores">
                                        <p class="text-muted">This chart shows users ranked by how consistently they participate in the chat.</p>
                                    </div>
                                </div>
            """
        
        # Close consistency card
        html += """
                            </div>
                        </div>
                        
                        <div class="card">
                            <div class="card-header">
                                <h2><i class="fas fa-user-slash"></i> Absence Analysis</h2>
                            </div>
                            <div class="card-body">
        """
        
        # Add absence stats
        if 'longest_absence' in stats:
            absence = stats['longest_absence']
            html += f"""
                                <div class="info-block">
                                    <h5>Longest Absence</h5>
                                    <p class="stat-value">{absence['user']}</p>
                                    <p>Was absent for {absence['details']['days']} days</p>
                                    <p>From {absence['details']['start_date'].strftime('%Y-%m-%d')} to {absence['details']['end_date'].strftime('%Y-%m-%d')}</p>
                                </div>
            """
            
        if 'users_with_absences' in stats and stats['users_with_absences']:
            html += """
                                <div class="mt-4">
                                    <h4>Users with Significant Absences (7+ days)</h4>
                                    <ul class="user-list">
            """
            
            for user in stats['users_with_absences']:
                html += f"""
                                        <li>{user}</li>
                """
                
            html += """
                                    </ul>
                                </div>
            """
        else:
            html += """
                                <p>No significant absences detected among active users.</p>
            """
        
        # Close absence card
        html += """
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <footer class="bg-light text-center p-3 mt-5">
                <p>Generated by Telegram Chat Analyzer</p>
            </footer>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """
        
        return html
    
    def _get_response_stats(self) -> Dict:
        """
        Analyze response patterns of users.
        
        Returns:
            Dictionary containing response pattern statistics
        """
        stats = {}
        
        # Calculate response rates for each user (when they are mentioned or replied to)
        user_response_rates = {}
        user_avg_response_times = {}
        
        for user in self.messages_df['from'].unique():
            # Messages that might need a response from this user
            messages_to_user = self.messages_df[
                (self.messages_df['next_message_user'] == user) & 
                (self.messages_df['from'] != user)
            ]
            
            total_messages_to_user = len(messages_to_user)
            
            if total_messages_to_user > 0:
                # Messages that this user responded to
                responses = messages_to_user[messages_to_user['time_until_next'] <= 60]  # Within 60 minutes
                response_rate = len(responses) / total_messages_to_user
                
                # Average response time
                avg_response_time = responses['time_until_next'].mean() if len(responses) > 0 else float('inf')
                
                user_response_rates[user] = response_rate
                user_avg_response_times[user] = avg_response_time
        
        # Users with fastest and slowest response times
        if user_avg_response_times:
            fastest_responder = min(user_avg_response_times.items(), key=lambda x: x[1])
            stats['fastest_responder'] = {
                'user': fastest_responder[0],
                'avg_time_minutes': fastest_responder[1]
            }
            
            # Find slowest excluding infinity values
            finite_response_times = {k: v for k, v in user_avg_response_times.items() if v != float('inf')}
            if finite_response_times:
                slowest_responder = max(finite_response_times.items(), key=lambda x: x[1])
                stats['slowest_responder'] = {
                    'user': slowest_responder[0],
                    'avg_time_minutes': slowest_responder[1]
                }
        
        # Users with highest and lowest response rates
        if user_response_rates:
            most_responsive = max(user_response_rates.items(), key=lambda x: x[1])
            least_responsive = min(user_response_rates.items(), key=lambda x: x[1])
            
            stats['most_responsive_user'] = {
                'user': most_responsive[0],
                'response_rate': most_responsive[1]
            }
            
            stats['least_responsive_user'] = {
                'user': least_responsive[0],
                'response_rate': least_responsive[1]
            }
        
        # Calculate ignored users (those whose messages frequently don't get responses)
        user_received_responses = {}
        for user in self.messages_df['from'].unique():
            messages_from_user = self.messages_df[self.messages_df['from'] == user]
            total_messages = len(messages_from_user)
            
            if total_messages > 0:
                received_responses = messages_from_user[messages_from_user['got_response'] == True]
                response_rate = len(received_responses) / total_messages
                user_received_responses[user] = response_rate
        
        if user_received_responses:
            # Filter to users with at least 10 messages
            active_users = {k: v for k, v in user_received_responses.items() 
                           if len(self.messages_df[self.messages_df['from'] == k]) >= 10}
            
            if active_users:
                most_ignored = min(active_users.items(), key=lambda x: x[1])
                stats['most_ignored_user'] = {
                    'user': most_ignored[0],
                    'got_response_rate': most_ignored[1]
                }
                
                most_engaging = max(active_users.items(), key=lambda x: x[1])
                stats['most_engaging_user'] = {
                    'user': most_engaging[0],
                    'got_response_rate': most_engaging[1]
                }
        
        return stats
    
    def _get_consistency_stats(self) -> Dict:
        """
        Analyze consistency of user activity patterns.
        
        Returns:
            Dictionary containing consistency statistics
        """
        stats = {}
        
        # Calculate daily activity consistency
        user_daily_consistency = {}
        total_days = (self.messages_df['day'].max() - self.messages_df['day'].min()).days + 1
        
        for user in self.messages_df['from'].unique():
            user_days = self.messages_df[self.messages_df['from'] == user]['day'].nunique()
            consistency_score = user_days / total_days if total_days > 0 else 0
            user_daily_consistency[user] = consistency_score
        
        if user_daily_consistency:
            most_consistent = max(user_daily_consistency.items(), key=lambda x: x[1])
            least_consistent = min(user_daily_consistency.items(), key=lambda x: x[1])
            
            stats['most_consistent_user'] = {
                'user': most_consistent[0],
                'consistency_score': most_consistent[1]
            }
            
            stats['least_consistent_user'] = {
                'user': least_consistent[0],
                'consistency_score': least_consistent[1]
            }
        
        # Calculate time of day consistency (variance in active hours)
        user_hour_variance = {}
        for user in self.messages_df['from'].unique():
            user_hours = self.messages_df[self.messages_df['from'] == user]['hour']
            if len(user_hours) > 5:  # Only for users with enough data
                hour_variance = user_hours.var()
                user_hour_variance[user] = hour_variance
        
        if user_hour_variance:
            most_consistent_time = min(user_hour_variance.items(), key=lambda x: x[1])
            least_consistent_time = max(user_hour_variance.items(), key=lambda x: x[1])
            
            stats['most_time_consistent_user'] = {
                'user': most_consistent_time[0],
                'hour_variance': most_consistent_time[1]
            }
            
            stats['least_time_consistent_user'] = {
                'user': least_consistent_time[0],
                'hour_variance': least_consistent_time[1]
            }
        
        return stats
    
    def _detect_user_absences(self) -> Dict:
        """
        Detect periods of absence for each user.
        
        Returns:
            Dictionary containing absence statistics
        """
        stats = {}
        
        # Find longest absence for each user
        user_absences = {}
        user_longest_absence = {}
        
        for user in self.messages_df['from'].unique():
            user_msgs = self.messages_df[self.messages_df['from'] == user].sort_values('date')
            
            if len(user_msgs) <= 1:
                continue
                
            # Calculate time gaps between consecutive messages
            date_diffs = user_msgs['date'].diff()
            
            # Find the longest gap
            max_gap_idx = date_diffs.idxmax()
            if pd.notna(max_gap_idx):
                max_gap = date_diffs.loc[max_gap_idx]
                
                # Only consider gaps of more than 3 days
                if max_gap.total_seconds() > 3 * 24 * 3600:
                    start_date = user_msgs.iloc[max_gap_idx-1]['date'] if max_gap_idx > 0 else None
                    end_date = user_msgs.loc[max_gap_idx, 'date']
                    
                    if start_date and end_date:
                        # Fix: Ensure start_date is before end_date
                        if start_date > end_date:
                            start_date, end_date = end_date, start_date
                            
                        absence_days = (end_date - start_date).days
                        
                        # Fix: Ensure we have positive absence days
                        if absence_days > 0:
                            user_longest_absence[user] = {
                                'start_date': start_date,
                                'end_date': end_date,
                                'days': absence_days
                            }
                            
                            # Track absences over 7 days
                            if absence_days >= 7:
                                user_absences[user] = absence_days
        
        if user_longest_absence:
            # Find user with longest absence
            longest_absence_user = max(user_longest_absence.items(), key=lambda x: x[1]['days'])
            stats['longest_absence'] = {
                'user': longest_absence_user[0],
                'details': longest_absence_user[1]
            }
            
            # Count users with significant absences
            stats['users_with_absences'] = list(user_absences.keys())
            stats['absence_count'] = len(user_absences)
        
        return stats
    
    def _identify_ghosters(self) -> Dict:
        """
        Identify users who are present but don't respond to others.
        
        Returns:
            Dictionary containing ghosting statistics
        """
        stats = {}
        
        # Calculate response rate and online presence for each user
        user_stats = {}
        
        for user in self.messages_df['from'].unique():
            # Messages sent by this user
            user_messages = len(self.messages_df[self.messages_df['from'] == user])
            
            # Messages this user could have responded to
            potential_responses = len(self.messages_df[
                (self.messages_df['next_message_user'] == user) & 
                (self.messages_df['from'] != user) &
                (self.messages_df['time_until_next'] <= 60)  # Within 60 minutes
            ])
            
            # Messages from others that this user actually responded to
            actual_responses = len(self.messages_df[
                (self.messages_df['from'] == user) & 
                (self.messages_df['is_response'] == True) &
                (self.messages_df['time_since_prev'] <= 60)  # Within 60 minutes
            ])
            
            response_rate = actual_responses / potential_responses if potential_responses > 0 else 0
            online_presence = user_messages / self.messages_df['from'].value_counts().sum()
            
            # Calculate ghosting score: high presence, low response
            if user_messages >= 10 and potential_responses >= 5:
                ghosting_score = online_presence * (1 - response_rate)
                
                user_stats[user] = {
                    'messages': user_messages,
                    'potential_responses': potential_responses,
                    'actual_responses': actual_responses,
                    'response_rate': response_rate,
                    'online_presence': online_presence,
                    'ghosting_score': ghosting_score
                }
        
        if user_stats:
            # Identify top ghosters
            top_ghosters = sorted(user_stats.items(), key=lambda x: x[1]['ghosting_score'], reverse=True)
            
            # Only include users with a significant ghosting score
            significant_ghosters = [user for user, data in top_ghosters if data['ghosting_score'] > 0.1]
            stats['top_ghosters'] = significant_ghosters[:3] if len(significant_ghosters) >= 3 else significant_ghosters
            
            # Identify most engaged users (high response rate)
            top_engaged = sorted(user_stats.items(), key=lambda x: x[1]['response_rate'], reverse=True)
            stats['most_engaged_users'] = [user for user, _ in top_engaged[:3]]
        
        return stats
    
    def generate_online_presence_visualizations(self) -> List[str]:
        """
        Generate visualizations for online presence analysis.
        
        Returns:
            List of generated visualization filenames
        """
        generated_viz = []
        
        try:
            # 1. User Activity Heatmap by Hour and Day
            plt.figure(figsize=(12, 8))
            user_day_hour = pd.crosstab(
                self.messages_df['day_of_week'], 
                self.messages_df['hour']
            )
            
            # Ensure days are in correct order
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            user_day_hour = user_day_hour.reindex(days_order)
            
            ax = sns.heatmap(user_day_hour, cmap='viridis', cbar_kws={'label': 'Message Count'})
            plt.title('User Activity by Hour and Day of Week')
            plt.xlabel('Hour of Day')
            plt.ylabel('Day of Week')
            plt.tight_layout()
            
            output_path = os.path.join(self.output_dir, 'user_activity_heatmap.png')
            plt.savefig(output_path)
            plt.close()
            generated_viz.append('user_activity_heatmap.png')
            
            # 2. User Time Period Preferences
            plt.figure(figsize=(12, 8))
            period_counts = {}
            
            for user in self.messages_df['from'].value_counts().nlargest(10).index:
                user_data = self.messages_df[self.messages_df['from'] == user]
                periods = user_data['time_period'].value_counts().reindex(['morning', 'afternoon', 'evening', 'night'], fill_value=0)
                period_counts[user] = periods
            
            if period_counts:
                pd.DataFrame(period_counts).T.plot(kind='bar', stacked=True, colormap='viridis')
                plt.title('Time Period Activity by User')
                plt.xlabel('User')
                plt.ylabel('Message Count')
                plt.legend(title='Time Period')
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                output_path = os.path.join(self.output_dir, 'user_time_preferences.png')
                plt.savefig(output_path)
                plt.close()
                generated_viz.append('user_time_preferences.png')
            
            # 3. Response Time Distribution
            plt.figure(figsize=(12, 8))
            response_times = self.messages_df[
                (self.messages_df['is_response'] == True) & 
                (self.messages_df['time_since_prev'] <= 60)  # Limit to 60 min for readability
            ]['time_since_prev']
            
            if not response_times.empty:
                sns.histplot(response_times, bins=30, kde=True)
                plt.axvline(response_times.median(), color='red', linestyle='--', 
                           label=f'Median: {response_times.median():.1f} min')
                plt.title('Response Time Distribution')
                plt.xlabel('Time to Respond (minutes)')
                plt.ylabel('Frequency')
                plt.legend()
                plt.tight_layout()
                
                output_path = os.path.join(self.output_dir, 'response_time_distribution.png')
                plt.savefig(output_path)
                plt.close()
                generated_viz.append('response_time_distribution.png')
            
            # 4. User Response Network
            self._generate_response_network()
            if os.path.exists(os.path.join(self.output_dir, 'user_response_network.png')):
                generated_viz.append('user_response_network.png')
            
            # 5. Ghosting Score Visualization
            plt.figure(figsize=(12, 8))
            
            ghosting_scores = {}
            for user in self.messages_df['from'].unique():
                # Messages sent by this user
                user_messages = len(self.messages_df[self.messages_df['from'] == user])
                
                # Only include users with sufficient activity
                if user_messages < 10:
                    continue
                
                # Messages this user could have responded to
                potential_responses = len(self.messages_df[
                    (self.messages_df['next_message_user'] == user) & 
                    (self.messages_df['from'] != user) &
                    (self.messages_df['time_until_next'] <= 60)
                ])
                
                # Messages this user actually responded to
                actual_responses = len(self.messages_df[
                    (self.messages_df['from'] == user) & 
                    (self.messages_df['is_response'] == True) &
                    (self.messages_df['time_since_prev'] <= 60)
                ])
                
                response_rate = actual_responses / potential_responses if potential_responses > 0 else 0
                online_presence = user_messages / self.messages_df['from'].value_counts().sum()
                
                # Calculate ghosting score
                if potential_responses >= 5:
                    ghosting_score = online_presence * (1 - response_rate) * 100  # Scale to 0-100
                    ghosting_scores[user] = ghosting_score
            
            if ghosting_scores:
                ghosting_df = pd.DataFrame({'User': list(ghosting_scores.keys()), 
                                         'Ghosting Score': list(ghosting_scores.values())})
                ghosting_df = ghosting_df.sort_values('Ghosting Score', ascending=False).head(10)
                
                ax = sns.barplot(x='Ghosting Score', y='User', data=ghosting_df, palette='viridis')
                plt.title('Top 10 Users by Ghosting Score')
                plt.xlabel('Ghosting Score (higher = more ghosting)')
                plt.tight_layout()
                
                output_path = os.path.join(self.output_dir, 'user_ghosting_scores.png')
                plt.savefig(output_path)
                plt.close()
                generated_viz.append('user_ghosting_scores.png')
                
            # 6. Consistency Visualization
            plt.figure(figsize=(12, 8))
            
            consistency_scores = {}
            total_days = (self.messages_df['day'].max() - self.messages_df['day'].min()).days + 1
            
            for user in self.messages_df['from'].unique():
                user_messages = len(self.messages_df[self.messages_df['from'] == user])
                
                # Only include users with sufficient activity
                if user_messages < 10:
                    continue
                
                user_days = self.messages_df[self.messages_df['from'] == user]['day'].nunique()
                daily_consistency = user_days / total_days if total_days > 0 else 0
                
                user_hours = self.messages_df[self.messages_df['from'] == user]['hour']
                hour_variance = user_hours.var() if len(user_hours) > 5 else float('nan')
                
                # Normalize hour variance to 0-1 range (lower is better)
                max_hour_variance = 24  # Theoretical maximum
                hour_consistency = 1 - (hour_variance / max_hour_variance) if not np.isnan(hour_variance) else float('nan')
                
                # Combined consistency score
                if not np.isnan(hour_consistency):
                    combined_score = (daily_consistency + hour_consistency) / 2 * 100  # Scale to 0-100
                    consistency_scores[user] = combined_score
            
            if consistency_scores:
                consistency_df = pd.DataFrame({'User': list(consistency_scores.keys()), 
                                           'Consistency Score': list(consistency_scores.values())})
                consistency_df = consistency_df.sort_values('Consistency Score', ascending=False)
                
                ax = sns.barplot(x='Consistency Score', y='User', data=consistency_df.head(10), palette='viridis')
                plt.title('Top 10 Users by Consistency Score')
                plt.xlabel('Consistency Score (higher = more consistent)')
                plt.tight_layout()
                
                output_path = os.path.join(self.output_dir, 'user_consistency_scores.png')
                plt.savefig(output_path)
                plt.close()
                generated_viz.append('user_consistency_scores.png')
            
        except Exception as e:
            self.logger.error(f"Error generating online presence visualizations: {str(e)}")
        
        return generated_viz
    
    def _generate_response_network(self):
        """Generate a network visualization of user responses"""
        try:
            import networkx as nx
            
            # Create directed graph
            G = nx.DiGraph()
            
            # Track who responds to whom
            response_counts = defaultdict(Counter)
            
            # Identify response pairs
            for i in range(1, len(self.messages_df)):
                curr_msg = self.messages_df.iloc[i]
                prev_msg = self.messages_df.iloc[i-1]
                
                # If message is a response and within 30 minutes
                if (curr_msg['from'] != prev_msg['from'] and 
                    curr_msg['time_since_prev'] <= 30):
                    response_counts[curr_msg['from']][prev_msg['from']] += 1
            
            # Add nodes for users
            for user in self.messages_df['from'].unique():
                G.add_node(user)
            
            # Add edges with weights based on response counts
            for responder, targets in response_counts.items():
                for target, count in targets.items():
                    if count >= 3:  # Only include significant response patterns
                        G.add_edge(responder, target, weight=count)
            
            # Draw the graph only if it has edges
            if G.number_of_edges() > 0:
                plt.figure(figsize=(12, 12))
                
                # Calculate node sizes based on message counts
                node_sizes = []
                for user in G.nodes():
                    count = len(self.messages_df[self.messages_df['from'] == user])
                    node_sizes.append(max(300, 30 * count / 10))
                
                # Calculate edge widths
                edge_widths = [G[u][v]['weight'] / 2 for u, v in G.edges()]
                
                # Use spring layout
                pos = nx.spring_layout(G, k=0.5, seed=42)
                
                # Draw nodes
                nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='skyblue', alpha=0.8)
                
                # Draw edges
                nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.5, edge_color='gray', 
                                      arrowsize=20, connectionstyle='arc3,rad=0.1')
                
                # Draw labels
                nx.draw_networkx_labels(G, pos, font_size=12, font_family='sans-serif')
                
                plt.title('User Response Network (Who Responds to Whom)')
                plt.axis('off')
                plt.tight_layout()
                plt.savefig(os.path.join(self.output_dir, 'user_response_network.png'))
                plt.close()
                
        except Exception as e:
            self.logger.error(f"Error generating response network: {str(e)}")