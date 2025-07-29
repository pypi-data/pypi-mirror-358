"""
Utility functions and shared dependencies for Telegram Analyzer.
"""

import nltk
import logging
import re
import emoji
from typing import Dict, List, Tuple, Any, Optional

# Set up logging
def setup_logging(level=logging.INFO):
    """Configure logging for the application"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

# Download required NLTK data
def download_nltk_data():
    """Download required NLTK data"""
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('vader_lexicon')

def extract_text_from_message(msg: Dict) -> str:
    """Extract text content from message"""
    text = msg.get('text', '')
    
    if isinstance(text, list):
        text_parts = []
        for item in text:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict) and 'text' in item:
                text_parts.append(item['text'])
        text = ' '.join(text_parts)
        
    return str(text).strip()

def has_emoji(text: str) -> bool:
    """Check if text contains emoji"""
    return bool(any(char in emoji.EMOJI_DATA for char in text))

def has_link(text: str) -> bool:
    """Check if text contains a URL"""
    return bool(re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text))
