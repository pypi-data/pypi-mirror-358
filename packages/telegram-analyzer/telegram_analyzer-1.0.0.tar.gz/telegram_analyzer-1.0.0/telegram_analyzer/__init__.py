# Update the __init__.py file to expose the OnlinePresenceAnalyzer

"""
Telegram Analyzer package
A toolkit for analyzing Telegram chat exports.
"""

__version__ = "1.0.0"

# Import key components to make them available at package level
from telegram_analyzer.parser import TelegramDataParser
from telegram_analyzer.analyzer import ChatAnalyzer
from telegram_analyzer.visualizer import Visualizer
from telegram_analyzer.report import ReportGenerator
from telegram_analyzer.online_presence_analyzer import OnlinePresenceAnalyzer  