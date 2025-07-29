"""
Setup script for the Telegram Analyzer package.
"""

from setuptools import setup, find_packages

setup(
    name="telegram-analyzer",
    version="1.0.0",
    packages=["telegram_analyzer"],
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0",
        "matplotlib>=3.1.0",
        "seaborn>=0.10.0",
        "nltk>=3.5.0",
        "tqdm>=4.0.0",
        "wordcloud>=1.8.0",
        "emoji>=1.2.0",
    ],
    extras_require={
        "interactive": [
            "plotly>=5.0.0",
            "networkx>=2.6.0",
            "scipy>=1.7.0"
        ],
        "web": [
            "flask>=3.0.0"
        ],
        "auth": [
            "flask>=3.0.0"
        ],
        "full": [
            "plotly>=5.0.0",
            "networkx>=2.6.0",
            "scipy>=1.7.0",
            "textblob>=0.15.0",
            "flask>3.0.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "telegram-analyzer=telegram_analyzer.main:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A toolkit for analyzing Telegram chat exports",
    keywords="telegram, analysis, visualization, chat",
    python_requires=">=3.7",
    # Add these lines for PEP 517 build system support
    use_scm_version=False,
    setup_requires=['setuptools>=42', 'wheel'],
    package_data={
        'telegram_analyzer': ['templates/*.html'],
    },
    include_package_data=True,
)