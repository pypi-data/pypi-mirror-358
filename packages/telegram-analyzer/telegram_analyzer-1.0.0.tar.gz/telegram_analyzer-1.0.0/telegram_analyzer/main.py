"""
Main entry point for the Telegram Analyzer application.
"""

import os
import argparse
import logging
from telegram_analyzer.utils import setup_logging, download_nltk_data
from telegram_analyzer.parser import TelegramDataParser
from telegram_analyzer.analyzer import ChatAnalyzer
from telegram_analyzer.visualizer import Visualizer
from telegram_analyzer.report import ReportGenerator
from telegram_analyzer.stats_export import export_stats_to_json
from telegram_analyzer.online_presence_analyzer import OnlinePresenceAnalyzer

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Telegram Chat Analyzer')
    parser.add_argument('input_file', nargs='?', help='Path to Telegram export JSON file')
    parser.add_argument('--output-dir', default='analysis_output', help='Output directory for analysis results')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level')
    
    # Web server arguments
    parser.add_argument('--serve', action='store_true', help='Start a web server to view the results')
    parser.add_argument('--host', default='127.0.0.1', help='Host to run the web server on')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the web server on')
    parser.add_argument('--no-browser', action='store_true', help="Don't open browser automatically when starting server")
    
    # Authentication arguments
    parser.add_argument('--user-db', default='users.json', help='Path to user database file')
    parser.add_argument('--no-auth', action='store_true', help='Disable authentication for web server')
    
    # Online presence analysis arguments
    parser.add_argument('--skip-online-presence', action='store_true', help='Skip online presence analysis')
    
    return parser.parse_args()

def main():
    """Main entry point for the application"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    log_level = getattr(logging, args.log_level)
    logger = setup_logging(log_level)
    
    # Start web server if requested
    if args.serve:
        try:
            from telegram_analyzer.web_server import run_server
            logger.info(f"Starting web server for directory: {args.output_dir}")
            success = run_server(
                args.output_dir, 
                args.host, 
                args.port, 
                not args.no_browser,
                args.user_db,
                not args.no_auth
            )
            return 0 if success else 1
        except ImportError:
            logger.error("Failed to start web server. Please install Flask with: pip install flask")
            return 1
    
    # Check if input file was provided
    if not args.input_file:
        logger.error("No input file provided. Use --serve to start the web server or provide an input file.")
        print("Usage: telegram-analyzer path/to/file.json [options]")
        print("       telegram-analyzer --serve [options]")
        return 1
    
    try:
        # Try to download NLTK data, but continue even if it fails
        nltk_success = download_nltk_data()
        if not nltk_success:
            logger.warning("NLTK data download failed or incomplete. Some text analysis features may be limited.")
            logger.warning("To manually download NLTK data, run:")
            logger.warning("import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')")
        
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)

        # Process messages
        logger.info("Processing messages...")
        data_parser = TelegramDataParser(args.input_file)
        messages_df = data_parser.process_messages()
        logger.info(f"Processed {len(messages_df)} messages")

        # Analyze chat
        logger.info("Analyzing chat...")
        analyzer = ChatAnalyzer(messages_df)
        analysis_results = analyzer.get_all_stats()
        
        # Run online presence analysis
        if not args.skip_online_presence:
            logger.info("Analyzing online presence patterns...")
            online_presence_dir = os.path.join(args.output_dir, 'online_presence')
            os.makedirs(online_presence_dir, exist_ok=True)
            
            try:
                online_analyzer = OnlinePresenceAnalyzer(messages_df, online_presence_dir)
                online_report_path = online_analyzer.generate_online_presence_report()
                online_presence_stats = online_analyzer.get_online_time_stats()
                
                # Add to overall analysis results
                analysis_results['online_presence'] = online_presence_stats
                
                if online_report_path:
                    logger.info(f"Online presence report generated at: {online_report_path}")
            except Exception as e:
                logger.error(f"Error in online presence analysis: {str(e)}", exc_info=True)
        
        # Export statistics to JSON for web server
        export_stats_to_json(analysis_results, args.output_dir)

        # Generate standard visualizations
        logger.info("Generating visualizations...")
        visualizer = Visualizer(messages_df, args.output_dir)
        generated_viz = visualizer.generate_all_visualizations()
        logger.info(f"Generated {len(generated_viz)} static visualizations: {', '.join(generated_viz)}")
        
        # Generate interactive visualizations if available
        interactive_viz = []
        try:
            from telegram_analyzer.enhanced_visualizer import EnhancedVisualizer
            logger.info("Generating interactive visualizations...")
            enhanced_viz = EnhancedVisualizer(messages_df, args.output_dir)
            interactive_viz = enhanced_viz.generate_all_visualizations()
            logger.info(f"Generated {len(interactive_viz)} interactive visualizations: {', '.join(interactive_viz)}")
        except ImportError:
            logger.info("Enhanced visualization module not available. Skipping interactive visualizations.")

        # Generate report
        logger.info("Generating report...")
        report_generator = ReportGenerator(analysis_results, args.output_dir)
        report_generator.generate_html_report(interactive_viz)

        logger.info(f"Analysis complete! Check the report at {args.output_dir}/report.html")
        
        # Optionally start the web server
        if args.serve:
            try:
                from telegram_analyzer.web_server import run_server
                logger.info("Starting web server...")
                run_server(
                    args.output_dir, 
                    args.host, 
                    args.port, 
                    not args.no_browser,
                    args.user_db,
                    not args.no_auth
                )
            except ImportError:
                logger.error("Failed to start web server. Please install Flask with: pip install flask")
                logger.info(f"You can view the report by opening {args.output_dir}/report.html in your browser.")
        
        return 0  # Success
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        return 1  # Error

if __name__ == "__main__":
    exit(main())