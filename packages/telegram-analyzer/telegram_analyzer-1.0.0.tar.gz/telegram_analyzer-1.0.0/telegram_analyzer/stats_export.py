"""
This module adds functionality to export analysis statistics to JSON for the web server.
"""

import os
import json
import logging
from datetime import datetime

def export_stats_to_json(stats, output_dir):
    """
    Export analysis statistics to a JSON file.
    
    Args:
        stats: Dictionary containing analysis statistics
        output_dir: Directory to save the JSON file
        
    Returns:
        Path to the saved JSON file or None if export failed
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Make sure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert datetime objects to strings
        stats_json = _convert_datetime_to_string(stats)
        
        # Define output path
        output_path = os.path.join(output_dir, 'stats.json')
        
        # Write JSON to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stats_json, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Statistics exported to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to export statistics to JSON: {str(e)}")
        return None

def _convert_datetime_to_string(obj):
    """
    Recursively convert datetime objects to strings in a nested dictionary or list.
    
    Args:
        obj: Object to convert (dictionary, list, or other)
        
    Returns:
        Object with datetime objects converted to strings
    """
    if isinstance(obj, dict):
        return {key: _convert_datetime_to_string(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_datetime_to_string(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj
