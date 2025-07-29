"""
Analyzes processed chat data.
"""

import pandas as pd
from typing import Dict
from nltk.corpus import stopwords
import logging
import nltk

class ChatAnalyzer:
    """Analyzes processed chat data"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the chat analyzer.
        
        Args:
            df: DataFrame containing processed chat messages
        """
        self.df = df
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Try to load stopwords
        try:
            nltk.download('stopwords', quiet=True)
            self.stop_words = set(stopwords.words('english'))
        except Exception as e:
            self.logger.warning(f"Could not load NLTK stopwords: {e}")
            self.stop_words = set()
        
        # Ensure date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(self.df['date']):
            self.df['date'] = pd.to_datetime(self.df['date'])

    def get_basic_stats(self) -> Dict:
        """Calculate basic chat statistics"""
        # Ensure text length column exists
        if 'text_length' not in self.df.columns:
            self.df['text_length'] = self.df['text'].str.len()
        
        return {
            'total_messages': len(self.df),
            'total_participants': self.df['from'].nunique(),
            'date_range': {
                'start': self.df['date'].min(),
                'end': self.df['date'].max(),
                'total_days': (self.df['date'].max() - self.df['date'].min()).days
            },
            'media_messages': self.df['media_type'].notna().sum(),
            'avg_message_length': self.df['text_length'].mean()
        }

    def get_user_stats(self) -> Dict:
        """Calculate user-specific statistics"""
        user_stats = {}
        
        # Ensure text length column exists
        if 'text_length' not in self.df.columns:
            self.df['text_length'] = self.df['text'].str.len()
        
        for user in self.df['from'].unique():
            user_messages = self.df[self.df['from'] == user]
            user_stats[user] = {
                'message_count': len(user_messages),
                'media_count': user_messages['media_type'].notna().sum(),
                'avg_message_length': user_messages['text_length'].mean(),
                'avg_sentiment': user_messages['sentiment'].mean() if 'sentiment' in self.df.columns else 0
            }
            
        return user_stats

    def get_activity_patterns(self) -> Dict:
        """Analyze activity patterns"""
        return {
            'hourly': self.df['date'].dt.hour.value_counts().sort_index().to_dict(),
            'daily': self.df['date'].dt.day_name().value_counts().to_dict(),
            'monthly': self.df['date'].dt.month.value_counts().sort_index().to_dict()
        }

    def get_content_analysis(self) -> Dict:
        """Analyze message content"""
        # Prepare default values for analysis
        media_types = self.df['media_type'].value_counts().to_dict() if 'media_type' in self.df.columns else {}
        
        # Check for emoji and link columns
        emoji_usage = self.df['has_emoji'].sum() if 'has_emoji' in self.df.columns else 0
        link_sharing = self.df['has_link'].sum() if 'has_link' in self.df.columns else 0
        
        return {
            'media_types': media_types,
            'avg_sentiment': self.df['sentiment'].mean() if 'sentiment' in self.df.columns else 0,
            'emoji_usage': emoji_usage,
            'link_sharing': link_sharing
        }
        
    def get_online_time_stats(self) -> Dict:
        """
        Calculate online time and presence statistics for users.
        
        Returns:
            Dictionary containing online time and presence statistics
        """
        try:
            # Compute user online time statistics
            user_online_times = {}
            peak_online_hours = {}
            
            for user in self.df['from'].unique():
                # Filter messages for this user
                user_messages = self.df[self.df['from'] == user]
                
                # Calculate total online time
                if len(user_messages) > 0:
                    # Total time from first to last message
                    total_time = (user_messages['date'].max() - user_messages['date'].min()).total_seconds() / 3600  # hours
                    
                    # Most active time (hour with most messages)
                    peak_hour = user_messages['date'].dt.hour.mode().values[0]
                    
                    # Hourly message distribution
                    hourly_distribution = user_messages['date'].dt.hour.value_counts().to_dict()
                    
                    user_online_times[user] = {
                        'total_hours': total_time,
                        'peak_time': f"{peak_hour:02d}:00",
                        'message_count': len(user_messages)
                    }
                    
                    peak_online_hours[user] = [
                        hourly_distribution.get(hour, 0) for hour in range(24)
                    ]
            
            # Compute overall statistics
            stats = {
                'user_online_times': user_online_times,
                'peak_online_hours': peak_online_hours,
                'total_active_users': len(user_online_times),
                'average_online_hours': sum(times['total_hours'] for times in user_online_times.values()) / len(user_online_times) if user_online_times else 0
            }
            
            return stats
        
        except Exception as e:
            self.logger.error(f"Error computing online time statistics: {str(e)}")
            return {}

    def get_all_stats(self) -> Dict:
        """Get all available statistics"""
        return {
            'basic_stats': self.get_basic_stats(),
            'user_stats': self.get_user_stats(),
            'activity_patterns': self.get_activity_patterns(),
            'content_analysis': self.get_content_analysis(),
            'online_time_stats': self.get_online_time_stats()
        }