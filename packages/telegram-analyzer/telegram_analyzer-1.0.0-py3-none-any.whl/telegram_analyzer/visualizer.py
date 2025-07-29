"""
Generates visualizations from analyzed data.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import networkx as nx
import logging
import emoji
from datetime import timedelta
import matplotlib.colors as mcolors

class Visualizer:
    """Generates visualizations from analyzed data"""
    
    def __init__(self, df: pd.DataFrame, output_dir: str):
        self.df = df
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        os.makedirs(output_dir, exist_ok=True)

    def generate_all_visualizations(self):
        """Generate all available visualizations"""
        successful_viz = []
        
        try:
            # Original visualizations
            if self._try_generate_visualization(self.generate_activity_heatmap):
                successful_viz.append('activity_heatmap.png')
                
            if self._try_generate_visualization(self.generate_user_activity_chart):
                successful_viz.append('user_activity.png')
                
            if self._try_generate_visualization(self.generate_sentiment_timeline):
                successful_viz.append('sentiment_timeline.png')
                
            if self._try_generate_visualization(self.generate_wordcloud):
                successful_viz.append('wordcloud.png')
                
            if self._try_generate_visualization(self.generate_media_distribution):
                successful_viz.append('media_distribution.png')
            
            # New visualizations
            if self._try_generate_visualization(self.generate_weekly_activity_chart):
                successful_viz.append('weekly_activity.png')
                
            if self._try_generate_visualization(self.generate_message_length_histogram):
                successful_viz.append('message_length_histogram.png')
                
            if self._try_generate_visualization(self.generate_response_time_analysis):
                successful_viz.append('response_time_analysis.png')
                
            if self._try_generate_visualization(self.generate_emoji_usage_chart):
                successful_viz.append('emoji_usage.png')
                
            if self._try_generate_visualization(self.generate_user_message_timeline):
                successful_viz.append('user_message_timeline.png')
                
            if self._try_generate_visualization(self.generate_topic_clusters):
                successful_viz.append('topic_clusters.png')
                
            if self._try_generate_visualization(self.generate_user_interaction_network):
                successful_viz.append('user_interaction_network.png')
                
            if self._try_generate_visualization(self.generate_word_frequency_chart):
                successful_viz.append('word_frequency.png')
                
            if self._try_generate_visualization(self.generate_sentiment_distribution):
                successful_viz.append('sentiment_distribution.png')
                
            if self._try_generate_visualization(self.generate_conversation_flow):
                successful_viz.append('conversation_flow.png')
            
            self.logger.info(f"Successfully generated {len(successful_viz)} visualizations")
            return successful_viz
            
        except Exception as e:
            self.logger.error(f"Error in generate_all_visualizations: {str(e)}")
            return successful_viz
            
    def _try_generate_visualization(self, viz_function):
        """Try to generate a visualization, catching and logging any errors"""
        try:
            viz_function()
            return True
        except Exception as e:
            func_name = viz_function.__name__
            self.logger.warning(f"Error in {func_name}: {str(e)}")
            return False

    def generate_activity_heatmap(self):
        """Generate activity heatmap"""
        self.logger.info("Generating activity heatmap")
        activity_pivot = pd.crosstab(
            self.df['date'].dt.day_name(),
            self.df['date'].dt.hour
        )
        
        plt.figure(figsize=(12, 6))
        sns.heatmap(activity_pivot, cmap='YlOrRd', cbar_kws={'label': 'Message Count'})
        plt.title('Message Activity Heatmap')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'activity_heatmap.png'))
        plt.close()

    def generate_user_activity_chart(self):
        """Generate user activity chart"""
        self.logger.info("Generating user activity chart")
        user_activity = self.df['from'].value_counts()
        
        plt.figure(figsize=(12, 6))
        user_activity.plot(kind='bar')
        plt.title('Messages per User')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'user_activity.png'))
        plt.close()

    def generate_sentiment_timeline(self):
        """Generate sentiment timeline"""
        self.logger.info("Generating sentiment timeline")
        daily_sentiment = self.df.groupby(self.df['date'].dt.date)['sentiment'].mean()
        
        plt.figure(figsize=(12, 6))
        daily_sentiment.plot(kind='line')
        plt.title('Sentiment Timeline')
        plt.xlabel('Date')
        plt.ylabel('Average Sentiment')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'sentiment_timeline.png'))
        plt.close()

    def generate_wordcloud(self):
        """Generate word cloud from messages"""
        self.logger.info("Generating wordcloud")
        text = ' '.join(self.df['text'].dropna())
        wordcloud = WordCloud(
            width=800, 
            height=400,
            background_color='white',
            stopwords=set(stopwords.words('english'))
        ).generate(text)
        
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.savefig(os.path.join(self.output_dir, 'wordcloud.png'))
        plt.close()

    def generate_media_distribution(self):
        """Generate media type distribution chart"""
        self.logger.info("Generating media distribution chart")
        if 'media_type' not in self.df.columns or self.df['media_type'].notna().sum() == 0:
            self.logger.warning("No media types found in data, skipping media distribution chart")
            return
            
        media_counts = self.df['media_type'].value_counts()
        
        plt.figure(figsize=(10, 6))
        media_counts.plot(kind='pie', autopct='%1.1f%%')
        plt.title('Media Type Distribution')
        plt.axis('equal')
        plt.savefig(os.path.join(self.output_dir, 'media_distribution.png'))
        plt.close()
        
    def generate_weekly_activity_chart(self):
        """Generate weekly activity chart showing message volume by day of week"""
        self.logger.info("Generating weekly activity chart")
        
        # Count messages by day of week
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = self.df['date'].dt.day_name().value_counts().reindex(days_order)
        
        plt.figure(figsize=(12, 6))
        ax = sns.barplot(x=day_counts.index, y=day_counts.values, palette='viridis')
        
        # Add value labels on top of bars
        for i, count in enumerate(day_counts.values):
            ax.text(i, count + 5, str(count), ha='center')
            
        plt.title('Message Activity by Day of Week')
        plt.xlabel('Day of Week')
        plt.ylabel('Number of Messages')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'weekly_activity.png'))
        plt.close()
        
    def generate_message_length_histogram(self):
        """Generate histogram of message lengths"""
        self.logger.info("Generating message length histogram")
        
        if 'text_length' not in self.df.columns:
            self.logger.warning("No text_length column found, skipping message length histogram")
            return
            
        plt.figure(figsize=(12, 6))
        
        # Filter out extreme outliers for better visualization
        text_lengths = self.df['text_length'].dropna()
        q99 = np.percentile(text_lengths, 99)
        filtered_lengths = text_lengths[text_lengths <= q99]
        
        sns.histplot(filtered_lengths, bins=30, kde=True)
        plt.axvline(filtered_lengths.mean(), color='r', linestyle='--', label=f'Mean: {filtered_lengths.mean():.1f}')
        plt.axvline(filtered_lengths.median(), color='g', linestyle='--', label=f'Median: {filtered_lengths.median():.1f}')
        
        plt.title('Distribution of Message Lengths')
        plt.xlabel('Message Length (characters)')
        plt.ylabel('Frequency')
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'message_length_histogram.png'))
        plt.close()
        
    def generate_response_time_analysis(self):
        """Generate analysis of response times between messages"""
        self.logger.info("Generating response time analysis")
        
        try:
            # Sort messages by date
            sorted_df = self.df.sort_values('date')
            
            # Calculate time differences between consecutive messages
            time_diffs = sorted_df['date'].diff().dropna()
            
            # Convert to minutes and filter out large gaps (e.g., > 24 hours)
            time_diffs_minutes = time_diffs.dt.total_seconds() / 60
            time_diffs_minutes = time_diffs_minutes[time_diffs_minutes < 24 * 60]  # Less than 24 hours
            
            plt.figure(figsize=(12, 6))
            
            # Create bins for response times
            bins = [0, 1, 5, 15, 30, 60, 120, 240, 480, 24 * 60]
            bin_labels = ['<1 min', '1-5 min', '5-15 min', '15-30 min', '30-60 min', 
                          '1-2 hrs', '2-4 hrs', '4-8 hrs', '8-24 hrs']
            
            # Count messages in each response time bin
            counts, _ = np.histogram(time_diffs_minutes, bins=bins)
            
            # Plot as a bar chart
            plt.bar(bin_labels, counts, color='skyblue')
            plt.title('Response Time Distribution')
            plt.xlabel('Time Between Messages')
            plt.ylabel('Number of Messages')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, 'response_time_analysis.png'))
            plt.close()
            
        except Exception as e:
            self.logger.warning(f"Error generating response time analysis: {str(e)}")
        
    def generate_emoji_usage_chart(self):
        """Generate chart of most commonly used emojis"""
        self.logger.info("Generating emoji usage chart")
        
        # Combine all messages
        all_text = ' '.join(self.df['text'].dropna().astype(str))
        
        # Extract emojis from text
        emoji_list = [c for c in all_text if c in emoji.EMOJI_DATA]
        
        if not emoji_list:
            self.logger.warning("No emojis found in data, skipping emoji usage chart")
            return
            
        # Count emoji frequencies
        emoji_counts = Counter(emoji_list).most_common(15)
        
        # Create a dataframe for easier plotting
        emoji_df = pd.DataFrame(emoji_counts, columns=['emoji', 'count'])
        
        plt.figure(figsize=(12, 8))
        ax = sns.barplot(x='count', y='emoji', data=emoji_df, palette='viridis')
        
        # Add value labels to bars
        for i, v in enumerate(emoji_df['count']):
            ax.text(v + 0.5, i, str(v), va='center')
            
        plt.title('Top 15 Most Used Emojis')
        plt.xlabel('Count')
        plt.ylabel('Emoji')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'emoji_usage.png'))
        plt.close()
        
    def generate_user_message_timeline(self):
        """Generate timeline showing message frequency by user over time"""
        self.logger.info("Generating user message timeline")
        
        # Get top 5 most active users
        top_users = self.df['from'].value_counts().nlargest(5).index.tolist()
        
        # Filter dataframe to include only top users
        filtered_df = self.df[self.df['from'].isin(top_users)]
        
        # Group by user and date (daily)
        user_daily = filtered_df.groupby([filtered_df['date'].dt.date, 'from']).size().unstack().fillna(0)
        
        # Plot time series
        plt.figure(figsize=(14, 8))
        
        for user in user_daily.columns:
            plt.plot(user_daily.index, user_daily[user], marker='o', markersize=4, linestyle='-', label=user)
            
        plt.title('Message Activity Timeline by User')
        plt.xlabel('Date')
        plt.ylabel('Number of Messages')
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'user_message_timeline.png'))
        plt.close()
        
    def generate_topic_clusters(self):
        """Generate word clusters to identify potential topics"""
        self.logger.info("Generating topic clusters")
        
        # Combine all messages
        all_text = ' '.join(self.df['text'].dropna().astype(str))
        
        # Tokenize and clean text
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(all_text.lower())
        filtered_words = [w for w in word_tokens if w.isalpha() and w not in stop_words and len(w) > 3]
        
        # Count word frequencies
        word_counts = Counter(filtered_words).most_common(50)
        
        # Create word cloud with different shape
        wordcloud = WordCloud(
            width=800, 
            height=400,
            background_color='white',
            colormap='viridis',
            contour_width=1,
            contour_color='steelblue',
            max_words=50,
            collocations=False
        ).generate_from_frequencies(dict(word_counts))
        
        plt.figure(figsize=(12, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Topic Word Clusters')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'topic_clusters.png'))
        plt.close()
        
          
    def generate_word_frequency_chart(self):
        """Generate chart of most frequently used words"""
        self.logger.info("Generating word frequency chart")
        
        # Combine all messages
        all_text = ' '.join(self.df['text'].dropna().astype(str))
        
        # Tokenize and clean text
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(all_text.lower())
        filtered_words = [w for w in word_tokens if w.isalpha() and w not in stop_words and len(w) > 3]
        
        # Count word frequencies
        word_counts = Counter(filtered_words).most_common(20)
        
        # Create a dataframe for easier plotting
        word_df = pd.DataFrame(word_counts, columns=['word', 'count'])
        
        plt.figure(figsize=(12, 8))
        ax = sns.barplot(x='count', y='word', data=word_df, palette='viridis')
        
        # Add value labels to bars
        for i, v in enumerate(word_df['count']):
            ax.text(v + 2, i, str(v), va='center')
            
        plt.title('Top 20 Most Used Words')
        plt.xlabel('Count')
        plt.ylabel('Word')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'word_frequency.png'))
        plt.close()
        
    def generate_sentiment_distribution(self):
        """Generate distribution of message sentiments"""
        self.logger.info("Generating sentiment distribution")
        
        if 'sentiment' not in self.df.columns:
            self.logger.warning("No sentiment column found, skipping sentiment distribution")
            return
            
        # Create sentiment categories
        self.df['sentiment_category'] = pd.cut(
            self.df['sentiment'], 
            bins=[-1.1, -0.6, -0.2, 0.2, 0.6, 1.1], 
            labels=['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive']
        )
        
        # Count by category
        sentiment_counts = self.df['sentiment_category'].value_counts().sort_index()
        
        # Plot as a donut chart
        plt.figure(figsize=(10, 8))
        
        # Create colors gradient from red to green
        colors = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']
        
        # Plot donut chart
        plt.pie(
            sentiment_counts, 
            labels=sentiment_counts.index, 
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            wedgeprops=dict(width=0.5, edgecolor='w')
        )
        
        plt.title('Distribution of Message Sentiments')
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'sentiment_distribution.png'))
        plt.close()
        
    def generate_conversation_flow(self):
        """Generate visualization of conversation flow throughout the day"""
        self.logger.info("Generating conversation flow visualization")
        
        # Group messages by hour and day of week
        hourly_flow = self.df.groupby([self.df['date'].dt.hour, self.df['date'].dt.day_name()]).size().unstack()
        
        # Reorder days
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hourly_flow = hourly_flow.reindex(columns=days_order)
        
        # Fill NaN with 0
        hourly_flow = hourly_flow.fillna(0)
        
        plt.figure(figsize=(14, 8))
        
        # Plot heatmap
        ax = sns.heatmap(
            hourly_flow, 
            cmap='YlGnBu', 
            linewidths=.5, 
            annot=True, 
            fmt='.0f',
            cbar_kws={'label': 'Number of Messages'}
        )
        
        plt.title('Conversation Flow Throughout the Day')
        plt.xlabel('Day of Week')
        plt.ylabel('Hour of Day (24-hour format)')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'conversation_flow.png'))
        plt.close()
    
    def generate_user_message_timeline(self):
        """Generate timeline showing message frequency by user over time"""
        self.logger.info("Generating user message timeline")
        
        try:
            # Get top 5 most active users
            top_users = self.df['from'].value_counts().nlargest(5).index.tolist()
            
            # Filter dataframe to include only top users
            filtered_df = self.df[self.df['from'].isin(top_users)]
            
            # Group by user and date (daily)
            # Ensure date column is properly converted to datetime
            if not pd.api.types.is_datetime64_any_dtype(filtered_df['date']):
                filtered_df['date'] = pd.to_datetime(filtered_df['date'])
                
            user_daily = filtered_df.groupby([filtered_df['date'].dt.date, 'from']).size().unstack().fillna(0)
            
            if user_daily.empty:
                self.logger.warning("No data for user message timeline, skipping visualization")
                return False
            
            # Plot time series
            plt.figure(figsize=(14, 8))
            
            for user in user_daily.columns:
                plt.plot(user_daily.index, user_daily[user], marker='o', markersize=4, linestyle='-', label=user)
                
            plt.title('Message Activity Timeline by User')
            plt.xlabel('Date')
            plt.ylabel('Number of Messages')
            plt.legend()
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, 'user_message_timeline.png'))
            plt.close()
            
            self.logger.info("User message timeline generated successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error generating user message timeline: {str(e)}")
            return False

    def generate_word_frequency_chart(self):
        """Generate chart of most frequently used words"""
        self.logger.info("Generating word frequency chart")
        
        try:
            # Combine all messages
            all_text = ' '.join(self.df['text'].dropna().astype(str))
            
            # Tokenize and clean text
            # Make sure stopwords is imported
            # from nltk.corpus import stopwords
            # from nltk.tokenize import word_tokenize
            
            try:
                from nltk.corpus import stopwords
                stop_words = set(stopwords.words('english'))
            except:
                self.logger.warning("NLTK stopwords not available, downloading now")
                import nltk
                nltk.download('stopwords')
                from nltk.corpus import stopwords
                stop_words = set(stopwords.words('english'))
                
            try:
                from nltk.tokenize import word_tokenize
            except:
                self.logger.warning("NLTK word_tokenize not available, downloading now")
                import nltk
                nltk.download('punkt')
                from nltk.tokenize import word_tokenize
            
            word_tokens = word_tokenize(all_text.lower())
            filtered_words = [w for w in word_tokens if w.isalpha() and w not in stop_words and len(w) > 3]
            
            if not filtered_words:
                self.logger.warning("No words found after filtering, skipping word frequency chart")
                return False
            
            # Count word frequencies
            from collections import Counter
            word_counts = Counter(filtered_words).most_common(20)
            
            # Create a dataframe for easier plotting
            word_df = pd.DataFrame(word_counts, columns=['word', 'count'])
            
            plt.figure(figsize=(12, 8))
            import seaborn as sns
            ax = sns.barplot(x='count', y='word', data=word_df, palette='viridis')
            
            # Add value labels to bars
            for i, v in enumerate(word_df['count']):
                ax.text(v + 2, i, str(v), va='center')
                
            plt.title('Top 20 Most Used Words')
            plt.xlabel('Count')
            plt.ylabel('Word')
            plt.tight_layout()
            
            output_path = os.path.join(self.output_dir, 'word_frequency.png')
            plt.savefig(output_path)
            plt.close()
            
            self.logger.info(f"Word frequency chart saved to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error generating word frequency chart: {str(e)}")
            return False
    
    def generate_conversation_flow(self):
        """Generate visualization of conversation flow throughout the day"""
        self.logger.info("Generating conversation flow visualization")
        
        try:
            # Make sure date column is properly converted to datetime
            if not pd.api.types.is_datetime64_any_dtype(self.df['date']):
                self.df['date'] = pd.to_datetime(self.df['date'])
                
            # Group messages by hour and day of week
            hourly_flow = self.df.groupby([self.df['date'].dt.hour, self.df['date'].dt.day_name()]).size().unstack()
            
            # Reorder days
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            hourly_flow = hourly_flow.reindex(columns=days_order)
            
            # Fill NaN with 0
            hourly_flow = hourly_flow.fillna(0)
            
            plt.figure(figsize=(14, 8))
            
            # Plot heatmap
            import seaborn as sns
            ax = sns.heatmap(
                hourly_flow, 
                cmap='YlGnBu', 
                linewidths=.5, 
                annot=True, 
                fmt='.0f',
                cbar_kws={'label': 'Number of Messages'}
            )
            
            plt.title('Conversation Flow Throughout the Day')
            plt.xlabel('Day of Week')
            plt.ylabel('Hour of Day (24-hour format)')
            plt.tight_layout()
            
            output_path = os.path.join(self.output_dir, 'conversation_flow.png')
            plt.savefig(output_path)
            plt.close()
            
            self.logger.info(f"Conversation flow visualization saved to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error generating conversation flow: {str(e)}")
            return False
    
    # Make sure these methods are added to the generate_all_visualizations method:
    
    def generate_all_visualizations(self):
        """Generate all available visualizations"""
        successful_viz = []
        
        try:
            # Original visualizations
            if self._try_generate_visualization(self.generate_activity_heatmap):
                successful_viz.append('activity_heatmap.png')
                
            if self._try_generate_visualization(self.generate_user_activity_chart):
                successful_viz.append('user_activity.png')
                
            if self._try_generate_visualization(self.generate_sentiment_timeline):
                successful_viz.append('sentiment_timeline.png')
                
            if self._try_generate_visualization(self.generate_wordcloud):
                successful_viz.append('wordcloud.png')
                
            if self._try_generate_visualization(self.generate_media_distribution):
                successful_viz.append('media_distribution.png')
            
            # Add the missing visualizations
            if self._try_generate_visualization(self.generate_word_frequency_chart):
                successful_viz.append('word_frequency.png')
                
            if self._try_generate_visualization(self.generate_user_message_timeline):
                successful_viz.append('user_message_timeline.png')
                
            if self._try_generate_visualization(self.generate_conversation_flow):
                successful_viz.append('conversation_flow.png')
            
            # Other visualizations...
            
            self.logger.info(f"Successfully generated {len(successful_viz)} visualizations")
            return successful_viz
                
        except Exception as e:
            self.logger.error(f"Error in generate_all_visualizations: {str(e)}")
            return successful_viz
        