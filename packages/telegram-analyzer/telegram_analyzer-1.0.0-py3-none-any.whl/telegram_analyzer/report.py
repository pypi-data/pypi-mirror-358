"""
Generates a unified, efficient analysis report including enhanced online presence data.
"""

import os
from typing import Dict, List, Optional
import logging
from datetime import datetime

class ReportGenerator:
    """Generates a unified, streamlined report with enhanced online presence analysis"""
    
    def __init__(self, stats: Dict, output_dir: str):
        """Initialize with analysis statistics and output directory"""
        self.stats = stats
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Ensure online presence stats are available
        if 'online_presence' not in self.stats:
            self.stats['online_presence'] = {}
        
        # Log available data sections for debugging
        self.logger.info(f"ReportGenerator initialized with data sections: {list(self.stats.keys())}")
    
    def generate_html_report(self, interactive_viz: Optional[List[str]] = None):
        """Generate a unified HTML report with all analysis sections"""
        self.logger.info("Generating comprehensive HTML report")
        try:
            # Check available visualizations
            visualizations = self._check_visualizations()
            
            # Create HTML content with all sections
            html_content = self._create_html_content(visualizations, interactive_viz or [])
            
            # Ensure output directory exists and write report
            os.makedirs(self.output_dir, exist_ok=True)
            report_path = os.path.join(self.output_dir, 'report.html')
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            self.logger.info(f"Unified report generated at {report_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return False
    
    def _check_visualizations(self) -> List[str]:
        """
        Check which visualization files exist in the output directory.
        
        Returns:
            List of available visualization filenames
        """
        visualizations = []
        
        # All possible visualization files to check
        viz_files = [
            # Basic visualizations
            'activity_heatmap.png', 'user_activity.png', 'wordcloud.png', 
            'sentiment_timeline.png', 'media_distribution.png', 
            'weekly_activity.png', 'conversation_flow.png',
            
            # Content analysis visualizations
            'word_frequency.png', 'topic_clusters.png', 
            'sentiment_distribution.png', 'message_length_histogram.png',
            
            # Online presence visualizations
            'user_time_preferences.png', 'user_online_hours.png', 
            'peak_online_hours.png', 'user_activity_heatmap.png',
            'user_ghosting_scores.png', 'user_consistency_scores.png',
            'response_time_distribution.png', 'user_response_network.png',
            
            # Interaction visualizations
            'user_interaction_network.png', 'response_time_analysis.png', 
            'emoji_usage.png'
        ]
        
        # Check each file
        for viz_file in viz_files:
            if os.path.exists(os.path.join(self.output_dir, viz_file)):
                visualizations.append(viz_file)
        
        self.logger.info(f"Found {len(visualizations)} visualization files")
        return visualizations
    
    def _create_html_content(self, visualizations: List[str], interactive_viz: List[str]) -> str:
        """Create HTML content for the unified report"""
        # Get data for the report
        basic_stats = self.stats.get('basic_stats', {})
        user_stats = self.stats.get('user_stats', {})
        activity_patterns = self.stats.get('activity_patterns', {})
        content_analysis = self.stats.get('content_analysis', {})
        online_presence = self.stats.get('online_presence', {})
        
        # Create HTML structure with Bootstrap CSS
        html = self._create_html_header()
        
        # Add content sections
        html += self._create_overview_section(basic_stats)
        html += self._create_user_activity_section(user_stats, visualizations)
        html += self._create_activity_patterns_section(activity_patterns, visualizations)
        html += self._create_content_analysis_section(visualizations)
        html += self._create_online_presence_section(online_presence, visualizations)
        html += self._create_interaction_section(visualizations)
        
        # Add footer and close HTML
        html += self._create_footer()
        
        return html
    
    def _create_html_header(self) -> str:
        """Create HTML header with necessary CSS and navigation"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Telegram Chat Analysis Report</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    padding-top: 70px;
                    color: #333;
                }
                .card {
                    margin-bottom: 20px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }
                .card-header {
                    background-color: #f8f9fa;
                    font-weight: bold;
                }
                .img-fluid {
                    max-width: 100%;
                    height: auto;
                    margin: 10px 0;
                    border-radius: 5px;
                }
                h1, h2, h3 {
                    color: #0d6efd;
                }
                .stat-value {
                    font-size: 1.2rem;
                    font-weight: bold;
                    color: #0d6efd;
                }
                .navbar {
                    background-color: #0d6efd;
                    color: white;
                }
                .section {
                    padding-top: 70px;
                    margin-top: -70px;
                }
                .info-block {
                    margin-bottom: 1rem;
                    padding: 0.5rem;
                    border-radius: 6px;
                    background-color: #e9ecef;
                }
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 1rem;
                }
                .user-list {
                    list-style-type: none;
                    padding-left: 0;
                }
                .user-list li {
                    padding: 0.5rem;
                    margin: 0.25rem 0;
                    background-color: #f1f3f5;
                    border-radius: 4px;
                }
            </style>
        </head>
        <body>
            <!-- Fixed navbar with navigation links -->
            <nav class="navbar navbar-expand-lg navbar-dark fixed-top">
                <div class="container-fluid">
                    <a class="navbar-brand" href="#"><i class="fas fa-comments"></i> Telegram Chat Analysis</a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav">
                            <li class="nav-item">
                                <a class="nav-link" href="#overview">Overview</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="#user-activity">User Activity</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="#activity-patterns">Activity Patterns</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="#content-analysis">Content Analysis</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="#online-presence">Online Presence</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="#interaction">Interaction</a>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>
            
            <div class="container">
        """
    
    def _create_overview_section(self, basic_stats: Dict) -> str:
        """Create overview section with basic statistics"""
        html = """
                <div id="overview" class="section">
                <div class="card">
                    <div class="card-header">
                        <h2><i class="fas fa-chart-bar"></i> Overview</h2>
                    </div>
                    <div class="card-body">
                        <div class="row">
        """
        
        if basic_stats:
            total_messages = basic_stats.get('total_messages', 0)
            total_participants = basic_stats.get('total_participants', 0)
            date_range = basic_stats.get('date_range', {})
            
            html += f"""
                            <div class="col-md-3 mb-3">
                                <div class="card">
                                    <div class="card-body text-center">
                                        <h5>Total Messages</h5>
                                        <p class="stat-value">{total_messages:,}</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-md-3 mb-3">
                                <div class="card">
                                    <div class="card-body text-center">
                                        <h5>Participants</h5>
                                        <p class="stat-value">{total_participants}</p>
                                    </div>
                                </div>
                            </div>
            """
            
            if date_range:
                total_days = date_range.get('total_days', 0)
                html += f"""
                            <div class="col-md-3 mb-3">
                                <div class="card">
                                    <div class="card-body text-center">
                                        <h5>Time Span</h5>
                                        <p class="stat-value">{total_days} days</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-md-3 mb-3">
                                <div class="card">
                                    <div class="card-body text-center">
                                        <h5>Avg. Message Length</h5>
                                        <p class="stat-value">{basic_stats.get('avg_message_length', 0):.1f} chars</p>
                                    </div>
                                </div>
                            </div>
                """
        
        html += """
                        </div>
                    </div>
                </div>
                </div>
        """
        return html
    
    def _create_user_activity_section(self, user_stats: Dict, visualizations: List[str]) -> str:
        """Create user activity section with top users"""
        html = """
                <div id="user-activity" class="section">
                <div class="card">
                    <div class="card-header">
                        <h2><i class="fas fa-users"></i> User Activity</h2>
                    </div>
                    <div class="card-body">
        """
        
        # Check for user_activity visualization
        if 'user_activity.png' in visualizations:
            html += """
                        <div class="row">
                            <div class="col-12">
                                <img src="user_activity.png" alt="User Activity" class="img-fluid">
                            </div>
                        </div>
            """
        
        # Add user stats
        if user_stats:
            top_users = sorted(user_stats.items(), key=lambda x: x[1]['message_count'], reverse=True)[:5]
            
            html += """
                        <div class="row mt-4">
                            <div class="col-12">
                                <h3>Top 5 Most Active Users</h3>
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>User</th>
                                            <th>Messages</th>
                                            <th>Media</th>
                                            <th>Avg. Length</th>
                                            <th>Sentiment</th>
                                        </tr>
                                    </thead>
                                    <tbody>
            """
            
            for user, stats in top_users:
                html += f"""
                                        <tr>
                                            <td>{user}</td>
                                            <td>{stats.get('message_count', 0):,}</td>
                                            <td>{stats.get('media_count', 0):,}</td>
                                            <td>{stats.get('avg_message_length', 0):.1f}</td>
                                            <td>{stats.get('avg_sentiment', 0):.2f}</td>
                                        </tr>
                """
            
            html += """
                                    </tbody>
                                </table>
                            </div>
                        </div>
            """
        
        html += """
                    </div>
                </div>
                </div>
        """
        return html
    
    def _create_activity_patterns_section(self, activity_patterns: Dict, visualizations: List[str]) -> str:
        """Create activity patterns section with visualizations"""
        html = """
                <div id="activity-patterns" class="section">
                <div class="card">
                    <div class="card-header">
                        <h2><i class="fas fa-clock"></i> Activity Patterns</h2>
                    </div>
                    <div class="card-body">
        """
        
        # Add activity visualizations
        for viz_file in ['activity_heatmap.png', 'weekly_activity.png', 'conversation_flow.png']:
            if viz_file in visualizations:
                html += f"""
                        <div class="row mb-4">
                            <div class="col-12">
                                <img src="{viz_file}" alt="{viz_file.replace('.png', '')}" class="img-fluid">
                            </div>
                        </div>
                """
        
        # Add activity patterns data
        if activity_patterns:
            hourly = activity_patterns.get('hourly', {})
            daily = activity_patterns.get('daily', {})
            
            if hourly and daily:
                most_active_hour = max(hourly.items(), key=lambda x: x[1])
                most_active_day = max(daily.items(), key=lambda x: x[1])
                
                html += f"""
                        <div class="row">
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-body text-center">
                                        <h5>Most Active Hour</h5>
                                        <p class="stat-value">{most_active_hour[0]}:00 ({most_active_hour[1]} messages)</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-body text-center">
                                        <h5>Most Active Day</h5>
                                        <p class="stat-value">{most_active_day[0]} ({most_active_day[1]} messages)</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                """
        
        html += """
                    </div>
                </div>
                </div>
        """
        return html
    
    def _create_content_analysis_section(self, visualizations: List[str]) -> str:
        """Create content analysis section with visualizations"""
        html = """
                <div id="content-analysis" class="section">
                <div class="card">
                    <div class="card-header">
                        <h2><i class="fas fa-file-alt"></i> Content Analysis</h2>
                    </div>
                    <div class="card-body">
        """
        
        # Add content visualizations
        for viz_file in ['wordcloud.png', 'word_frequency.png', 'topic_clusters.png', 
                        'sentiment_distribution.png', 'message_length_histogram.png']:
            if viz_file in visualizations:
                html += f"""
                        <div class="row mb-4">
                            <div class="col-12">
                                <img src="{viz_file}" alt="{viz_file.replace('.png', '')}" class="img-fluid">
                            </div>
                        </div>
                """
        
        # Add media distribution if available
        if 'media_distribution.png' in visualizations:
            html += """
                        <div class="row">
                            <div class="col-md-6 offset-md-3">
                                <h3 class="text-center">Media Types</h3>
                                <img src="media_distribution.png" alt="Media Distribution" class="img-fluid">
                            </div>
                        </div>
            """
        
        html += """
                    </div>
                </div>
                </div>
        """
        return html
    
    def _create_online_presence_section(self, online_presence: Dict, visualizations: List[str]) -> str:
        """Create comprehensive online presence section with all visualizations and stats"""
        html = """
            <div id="online-presence" class="section">
            <div class="card">
                <div class="card-header">
                    <h2><i class="fas fa-user-clock"></i> Online Presence Analysis</h2>
                    <a href="online_presence/online_presence_report.html" target="_blank" class="btn btn-sm btn-primary float-end">
                        View Detailed Report <i class="fas fa-external-link-alt"></i>
                    </a>
                </div>
                <div class="card-body">
    """
        
        if online_presence:
            # Activity overview grid
            html += """<div class="stats-grid">"""
            
            # Most/least active users by days
            if 'most_active_user_days' in online_presence:
                most_active = online_presence['most_active_user_days']
                html += f"""
                            <div class="info-block">
                                <h5>Most Active User</h5>
                                <p class="stat-value">{most_active['user']}</p>
                                <p>Active for {most_active['active_days']} days</p>
                            </div>
                """
                
            if 'least_active_user_days' in online_presence:
                least_active = online_presence['least_active_user_days']
                html += f"""
                            <div class="info-block">
                                <h5>Least Active User</h5>
                                <p class="stat-value">{least_active['user']}</p>
                                <p>Active for only {least_active['active_days']} days</p>
                            </div>
                """
            
            # Day activity stats
            if 'most_active_day' in online_presence and 'least_active_day' in online_presence:
                html += f"""
                            <div class="info-block">
                                <h5>Most Active Day</h5>
                                <p class="stat-value">{online_presence['most_active_day']}</p>
                            </div>
                            <div class="info-block">
                                <h5>Least Active Day</h5>
                                <p class="stat-value">{online_presence['least_active_day']}</p>
                            </div>
                """
            
            html += """</div>"""
            
            # Time Period Preferences - Early Birds and Night Owls
            if 'early_birds' in online_presence or 'night_owls' in online_presence:
                html += """
                        <h3 class="mt-4"><i class="fas fa-clock"></i> Time Preferences</h3>
                        <div class="row">
                """
                
                if 'early_birds' in online_presence:
                    html += """
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header">
                                        <h5><i class="fas fa-sun"></i> Morning People (Early Birds)</h5>
                                    </div>
                                    <div class="card-body">
                                        <ul class="user-list">
                    """
                    
                    for user in online_presence['early_birds']:
                        html += f"""
                                            <li>{user}</li>
                        """
                        
                    html += """
                                        </ul>
                                    </div>
                                </div>
                            </div>
                    """
                    
                if 'night_owls' in online_presence:
                    html += """
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header">
                                        <h5><i class="fas fa-moon"></i> Night Owls</h5>
                                    </div>
                                    <div class="card-body">
                                        <ul class="user-list">
                    """
                    
                    for user in online_presence['night_owls']:
                        html += f"""
                                            <li>{user}</li>
                        """
                        
                    html += """
                                        </ul>
                                    </div>
                                </div>
                            </div>
                    """
                
                html += """
                        </div>
                """
            
            # User Preferred Time Periods
            if 'user_preferred_periods' in online_presence:
                time_period_labels = {
                    'morning': 'Morning (5 AM - 12 PM)',
                    'afternoon': 'Afternoon (12 PM - 5 PM)',
                    'evening': 'Evening (5 PM - 10 PM)',
                    'night': 'Night (10 PM - 5 AM)'
                }
                
                html += """
                        <div class="row mt-4">
                            <div class="col-12">
                                <h4>User Time Period Preferences</h4>
                                <div class="row">
                """
                
                for period in ['morning', 'afternoon', 'evening', 'night']:
                    users = [user for user, pref in online_presence['user_preferred_periods'].items() if pref == period]
                    if users:
                        html += f"""
                                    <div class="col-md-3">
                                        <h5>{time_period_labels.get(period, period.title())}</h5>
                                        <ul class="user-list">
                        """
                        
                        # Show top users for each period (limit to 5 for space)
                        for user in users[:5]:
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
            
            # Add activity visualizations - activity heatmap, time preferences
            for viz_file in ['user_activity_heatmap.png', 'user_time_preferences.png']:
                if viz_file in visualizations:
                    viz_title = ' '.join(viz_file.replace('.png', '').split('_')).title()
                    html += f"""
                        <div class="row mt-4">
                            <div class="col-12">
                                <h4>{viz_title}</h4>
                                <img src="{viz_file}" class="img-fluid" alt="{viz_title}">
                            </div>
                        </div>
                    """
            
            # User Online Times section with detailed cards
            if 'user_online_times' in online_presence:
                html += """
                        <h3 class="mt-4"><i class="fas fa-hourglass-half"></i> User Online Time</h3>
                        <div class="row">
                """
                
                # Create a card for each user with their online time stats
                for user, times in online_presence['user_online_times'].items():
                    html += f"""
                            <div class="col-md-4 mb-3">
                                <div class="card">
                                    <div class="card-body">
                                        <h5>{user}</h5>
                                        <p>Total Online Hours: {times.get('total_hours', 0):.2f}</p>
                                        <p>Most Active Time: {times.get('peak_time', 'N/A')}</p>
                                        <p>Messages: {times.get('message_count', 0)}</p>
                                    </div>
                                </div>
                            </div>
                    """
                    
                html += """
                        </div>
                """
            
            # User Online Hours Visualizations
            for viz_file in ['user_online_hours.png', 'peak_online_hours.png']:
                if viz_file in visualizations:
                    viz_title = ' '.join(viz_file.replace('.png', '').split('_')).title()
                    html += f"""
                        <div class="row mt-4">
                            <div class="col-12">
                                <h4>{viz_title}</h4>
                                <img src="{viz_file}" class="img-fluid" alt="{viz_title}">
                                <p class="text-muted mt-2">
                                    {
                                    "User Online Hours": "Shows total time users spend active in the chat.", 
                                    "Peak Online Hours": "Shows which hours of the day each user is most active."
                                    }.get(viz_title, "")
                                </p>
                            </div>
                        </div>
                    """
            
            # Response Patterns section with comprehensive stats
            html += """
                    <h3 class="mt-4"><i class="fas fa-reply"></i> Response Patterns</h3>
                    <div class="stats-grid">
            """
            
            # Add response stats with comprehensive formatting
            response_stats = [
                ('fastest_responder', 'Fastest Responder', lambda s: f"{s['user']} ({s['avg_time_minutes']:.1f} min)"),
                ('slowest_responder', 'Slowest Responder', lambda s: f"{s['user']} ({s['avg_time_minutes']:.1f} min)"),
                ('most_responsive_user', 'Most Responsive User', lambda s: f"{s['user']} ({s['response_rate'] * 100:.1f}%)"),
                ('least_responsive_user', 'Least Responsive User', lambda s: f"{s['user']} ({s['response_rate'] * 100:.1f}%)"),
                ('most_ignored_user', 'Most Ignored User', lambda s: f"{s['user']} ({s['got_response_rate'] * 100:.1f}%)"),
                ('most_engaging_user', 'Most Engaging User', lambda s: f"{s['user']} ({s['got_response_rate'] * 100:.1f}%)")
            ]
            
            for key, title, formatter in response_stats:
                if key in online_presence:
                    html += f"""
                            <div class="info-block">
                                <h5>{title}</h5>
                                <p class="stat-value">{formatter(online_presence[key])}</p>
                            </div>
                    """
                    
            html += """
                    </div>
            """
            
            # Response Visualizations
            for viz_file in ['response_time_distribution.png', 'user_response_network.png']:
                if viz_file in visualizations:
                    viz_title = ' '.join(viz_file.replace('.png', '').split('_')).title()
                    html += f"""
                        <div class="row mt-4">
                            <div class="col-12">
                                <h4>{viz_title}</h4>
                                <img src="{viz_file}" class="img-fluid" alt="{viz_title}">
                                <p class="text-muted mt-2">
                                    {
                                    "Response Time Distribution": "Shows how quickly users respond to messages.", 
                                    "User Response Network": "Shows who responds to whom in the conversation."
                                    }.get(viz_title, "")
                                </p>
                            </div>
                        </div>
                    """
            
            # Ghosting Analysis section
            if 'top_ghosters' in online_presence or 'most_engaged_users' in online_presence or 'user_ghosting_scores.png' in visualizations:
                html += """
                        <h3 class="mt-4"><i class="fas fa-ghost"></i> "Ghosting" Analysis</h3>
                        <p>
                            This analysis identifies users who are present in the chat but tend not to respond to others.
                            A high "ghosting" score means a user reads messages but rarely responds.
                        </p>
                """
                
                if 'top_ghosters' in online_presence or 'most_engaged_users' in online_presence:
                    html += """
                        <div class="row">
                    """
                    
                    if 'top_ghosters' in online_presence:
                        html += """
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header">
                                        <h5>Top "Ghosters"</h5>
                                    </div>
                                    <div class="card-body">
                                        <ul class="user-list">
                        """
                        
                        for user in online_presence['top_ghosters']:
                            html += f"""
                                            <li><i class="fas fa-ghost"></i> {user}</li>
                            """
                            
                        html += """
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        """
                        
                    if 'most_engaged_users' in online_presence:
                        html += """
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header">
                                        <h5>Most Engaged Users</h5>
                                    </div>
                                    <div class="card-body">
                                        <ul class="user-list">
                        """
                        
                        for user in online_presence['most_engaged_users']:
                            html += f"""
                                            <li><i class="fas fa-comments"></i> {user}</li>
                            """
                            
                        html += """
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        """
                        
                    html += """
                        </div>
                    """
                
                # Ghosting visualization
                if 'user_ghosting_scores.png' in visualizations:
                    html += """
                        <div class="row mt-3">
                            <div class="col-12">
                                <img src="user_ghosting_scores.png" class="img-fluid" alt="User Ghosting Scores">
                                <p class="text-muted mt-2">Chart shows users ranked by their tendency to "ghost" (be present but not respond to messages).</p>
                            </div>
                        </div>
                    """
            
            # Consistency Analysis
            consistency_viz_exists = 'user_consistency_scores.png' in visualizations
            consistency_stats_exist = any(key in online_presence for key in 
                                        ['most_consistent_user', 'least_consistent_user', 
                                         'most_time_consistent_user', 'least_time_consistent_user'])
            
            if consistency_viz_exists or consistency_stats_exist:
                html += """
                        <h3 class="mt-4"><i class="fas fa-calendar-check"></i> Consistency Analysis</h3>
                        <p>This analysis measures how consistently users participate in the chat over time.</p>
                """
                
                if consistency_stats_exist:
                    html += """
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
                        if key in online_presence:
                            html += f"""
                            <div class="info-block">
                                <h5>{title}</h5>
                                <p class="stat-value">{formatter(online_presence[key])}</p>
                            </div>
                            """
                            
                    html += """
                        </div>
                    """
                    
                # Consistency visualization
                if consistency_viz_exists:
                    html += """
                        <div class="row mt-3">
                            <div class="col-12">
                                <img src="user_consistency_scores.png" class="img-fluid" alt="User Consistency Scores">
                                <p class="text-muted mt-2">Higher scores indicate more consistent participation patterns.</p>
                            </div>
                        </div>
                    """
            
            # Absence Analysis section
            absence_stats_exist = 'longest_absence' in online_presence or ('users_with_absences' in online_presence and online_presence['users_with_absences'])
            
            if absence_stats_exist:
                html += """
                        <h3 class="mt-4"><i class="fas fa-user-slash"></i> Absence Analysis</h3>
                        <p>This analysis detects periods when users were absent from the chat for extended periods.</p>
                """
                
                if 'longest_absence' in online_presence:
                    absence = online_presence['longest_absence']
                    html += f"""
                        <div class="info-block">
                            <h5>Longest Absence</h5>
                            <p class="stat-value">{absence['user']}</p>
                            <p>Was absent for {absence['details']['days']} days</p>
                            <p>From {absence['details']['start_date'].strftime('%Y-%m-%d')} to {absence['details']['end_date'].strftime('%Y-%m-%d')}</p>
                        </div>
                    """
                    
                if 'users_with_absences' in online_presence and online_presence['users_with_absences']:
                    html += """
                        <div class="mt-3">
                            <h5>Users with Significant Absences (7+ days)</h5>
                            <ul class="user-list">
                    """
                    
                    for user in online_presence['users_with_absences']:
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
                    
        else:
            html += """
                <div class="alert alert-info">
                    <h4><i class="fas fa-info-circle"></i> No Online Presence Data Available</h4>
                    <p>Online presence analysis was not performed or no data was found.</p>
                </div>
            """
            
        html += """
                    </div>
                </div>
                </div>
        """
        return html
    
    def _create_interaction_section(self, visualizations: List[str]) -> str:
        """Create interaction analysis section with network visualizations"""
        html = """
                <div id="interaction" class="section">
                <div class="card">
                    <div class="card-header">
                        <h2><i class="fas fa-network-wired"></i> Interaction Analysis</h2>
                    </div>
                    <div class="card-body">
        """
        
        interaction_viz_exists = False
        
        # Add interaction visualizations
        for viz_file in ['user_interaction_network.png', 'response_time_analysis.png', 'emoji_usage.png']:
            if viz_file in visualizations:
                interaction_viz_exists = True
                viz_title = ' '.join(viz_file.replace('.png', '').split('_')).title()
                html += f"""
                        <div class="row mb-4">
                            <div class="col-12">
                                <h3>{viz_title}</h3>
                                <img src="{viz_file}" alt="{viz_file.replace('.png', '')}" class="img-fluid">
                            </div>
                        </div>
                """
        
        if not interaction_viz_exists:
            html += """
                    <div class="alert alert-info">
                        <h4><i class="fas fa-info-circle"></i> No Interaction Analysis Available</h4>
                        <p>Interaction analysis was not performed or no visualizations were found.</p>
                    </div>
            """
        
        html += """
                    </div>
                </div>
                </div>
        """
        return html
    
    def _create_footer(self) -> str:
        """Create footer with JavaScript for smooth scrolling"""
        return f"""
            </div>
            
            <footer class="bg-light text-center py-3 mt-5">
                <div class="container">
                    <p class="mb-0">Generated by Telegram Chat Analyzer on {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                </div>
            </footer>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
            <script>
                // Add smooth scrolling for navigation links
                document.querySelectorAll('nav a.nav-link').forEach(anchor => {{
                    anchor.addEventListener('click', function(e) {{
                        e.preventDefault();
                        
                        const targetId = this.getAttribute('href');
                        const targetElement = document.querySelector(targetId);
                        
                        window.scrollTo({{
                            top: targetElement.offsetTop - 60,
                            behavior: 'smooth'
                        }});
                    }});
                }});
            </script>
        </body>
        </html>
        """