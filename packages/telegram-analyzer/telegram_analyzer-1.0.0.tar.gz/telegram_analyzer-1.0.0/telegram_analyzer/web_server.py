"""
Web server module for Telegram Analyzer.
This module provides a Flask web application to serve the analysis results interactively.
Enforces user flow: register -> login -> analyze
"""

import os
import logging
import webbrowser
import threading
import time
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps

# Check if Flask is available
try:
    import flask
    from flask import Flask, request, redirect, url_for, render_template, send_from_directory, jsonify
    from flask import session, flash, make_response
    from werkzeug.utils import secure_filename
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

class AnalyzerWebServer:
    """Web server for the Telegram Analyzer"""
    
    def __init__(self, output_dir, host='127.0.0.1', port=5000, open_browser=True, 
                 user_db_path=None, enable_auth=True):
        """
        Initialize the web server.
        
        Args:
            output_dir: Directory containing analysis results
            host: Host to run the server on
            port: Port to run the server on
            open_browser: Whether to automatically open the browser
            user_db_path: Path to user database file
            enable_auth: Whether to enable authentication
        """
        if not FLASK_AVAILABLE:
            raise ImportError(
                "Flask is not available. Please install it with: pip install flask"
            )
            
        self.output_dir = os.path.abspath(output_dir)
        self.host = host
        self.port = port
        self.open_browser = open_browser
        self.logger = logging.getLogger(__name__)
        self.upload_folder = os.path.join(tempfile.gettempdir(), 'telegram_analyzer_uploads')
        self.enable_auth = True  # Always enable auth to enforce user flow
        self.user_db_path = user_db_path or os.path.join(os.path.dirname(__file__), 'users.json')
        
        os.makedirs(self.upload_folder, exist_ok=True)
        
        # Initialize authentication
        try:
            from telegram_analyzer.auth import get_auth_handler
            self.auth = get_auth_handler(self.user_db_path)
            self.logger.info(f"Authentication enabled with user database: {self.user_db_path}")
        except ImportError:
            self.logger.error("Auth module not available. This is required for the application.")
            raise ImportError(
                "Authentication module is required. Please ensure telegram_analyzer.auth is available."
            )
        
        self.app = self._create_app()
        
    def _create_app(self):
        """Create Flask application"""
        app = Flask(__name__)
        app.secret_key = os.urandom(24)  # For session and flash messages
        app.config['UPLOAD_FOLDER'] = self.upload_folder
        app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB max upload
        app.config['OUTPUT_DIR'] = self.output_dir
        app.config['ENABLE_AUTH'] = self.enable_auth
        
        # Authentication middleware
        def login_required(func):
            @wraps(func)
            def decorated_function(*args, **kwargs):
                session_id = request.cookies.get('session_id')
                if not session_id:
                    flash('Please log in to access this page', 'warning')
                    return redirect(url_for('login', next=request.url))
                    
                valid, username = self.auth.verify_session(session_id)
                if not valid:
                    flash('Your session has expired. Please log in again', 'warning')
                    return redirect(url_for('login', next=request.url))
                    
                return func(*args, **kwargs)
            return decorated_function
            
        # Define routes
        @app.route('/')
        def index():
            """Main index route - redirects to login if not authenticated"""
            # Check if the user is logged in
            session_id = request.cookies.get('session_id')
            if session_id:
                valid, username = self.auth.verify_session(session_id)
                if valid:
                    # User is logged in, show dashboard
                    report_path = os.path.join(self.output_dir, 'report.html')
                    
                    if session.get('analysis_running', False):
                        return render_template('index.html', 
                                              username=username,
                                              analysis_running=True)
                    
                    if os.path.exists(report_path):
                        return render_template('index.html', 
                                              username=username,
                                              report_available=True)
                    else:
                        return render_template('index.html', 
                                              username=username, 
                                              upload_prompt=True)
            
            # Not logged in, redirect to login page
            return redirect('/login')
        
        @app.route('/login', methods=['GET', 'POST'])
        def login():
            """Login page"""
            # Check if already logged in
            session_id = request.cookies.get('session_id')
            if session_id:
                valid, _ = self.auth.verify_session(session_id)
                if valid:
                    return redirect('/')
                
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                remember = 'remember' in request.form
                
                success, message, session_id = self.auth.authenticate(username, password)
                
                if success:
                    # Create response with redirect
                    next_url = request.args.get('next', '/')
                    resp = make_response(redirect(next_url))
                    
                    # Set session cookie
                    max_age = 30 * 24 * 60 * 60 if remember else None  # 30 days if remember, else session
                    resp.set_cookie('session_id', session_id, httponly=True, max_age=max_age)
                    
                    # Return response
                    flash('Login successful', 'success')
                    return resp
                else:
                    return render_template('login.html', error=message)
            
            return render_template('login.html')
        
        @app.route('/api/login', methods=['POST'])
        def api_login():
            """API endpoint for login validation"""
            username = request.form.get('username')
            password = request.form.get('password')
            remember = 'remember' in request.form
                
            success, message, session_id = self.auth.authenticate(username, password)
            
            if success:
                response = jsonify({"success": True, "redirect": "/"})
                max_age = 30 * 24 * 60 * 60 if remember else None  # 30 days if remember, else session
                response.set_cookie('session_id', session_id, httponly=True, max_age=max_age)
                return response
            else:
                return jsonify({"success": False, "message": message})
            
        @app.route('/register', methods=['GET', 'POST'])
        def register():
            """Register page"""
            # Check if already logged in
            session_id = request.cookies.get('session_id')
            if session_id:
                valid, _ = self.auth.verify_session(session_id)
                if valid:
                    return redirect('/')
                
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                confirm_password = request.form.get('confirm_password')
                email = request.form.get('email')
                
                # Check if passwords match
                if password != confirm_password:
                    return render_template('register.html', error="Passwords do not match")
                
                # Register user
                success, message = self.auth.register_user(username, password, email)
                
                if success:
                    flash('Registration successful. Please log in.', 'success')
                    return redirect('/login')
                else:
                    return render_template('register.html', error=message)
            
            return render_template('register.html')
            
        @app.route('/logout')
        def logout():
            """Logout route"""
            session_id = request.cookies.get('session_id')
            if session_id:
                self.auth.logout(session_id)
                
            resp = make_response(redirect('/login'))
            resp.set_cookie('session_id', '', expires=0)
            
            flash('Logged out successfully', 'success')
            return resp
            
        @app.route('/account')
        @login_required
        def account():
            """User account page"""
            session_id = request.cookies.get('session_id')
            valid, username = self.auth.verify_session(session_id)
            
            if not valid:
                return redirect('/login')
                
            # Get user information
            user_info = self.auth.users.get(username, {})
            email = user_info.get('email', '')
            created_at = datetime.fromisoformat(user_info.get('created_at', datetime.now().isoformat()))
            last_login = user_info.get('last_login')
            
            if last_login:
                last_login = datetime.fromisoformat(last_login)
                last_login_days = (datetime.now() - last_login).days
            else:
                last_login_days = 0
                
            # Get user analyses
            analyses = []
            save_analyses = user_info.get('save_analyses', True)
            
            # In a real implementation, you would fetch the user's analyses from a database
            # For now, just show a dummy analysis
            analyses.append({
                'id': '1',
                'name': 'Sample Analysis',
                'date': datetime.now().strftime('%Y-%m-%d %H:%M')
            })
            
            return render_template('account.html',
                                  username=username,
                                  email=email,
                                  created_at=created_at.strftime('%Y-%m-%d'),
                                  analyses_count=len(analyses),
                                  last_login_days=last_login_days,
                                  analyses=analyses,
                                  save_analyses=save_analyses)
                                  
        @app.route('/account/password', methods=['POST'])
        @login_required
        def change_password():
            """Change password"""
            session_id = request.cookies.get('session_id')
            valid, username = self.auth.verify_session(session_id)
            
            if not valid:
                return redirect('/login')
                
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_new_password = request.form.get('confirm_new_password')
            
            # Check if new passwords match
            if new_password != confirm_new_password:
                flash('New passwords do not match', 'error')
                return redirect('/account')
                
            # Change password
            success, message = self.auth.change_password(username, current_password, new_password)
            
            if success:
                flash('Password changed successfully', 'success')
            else:
                flash(message, 'error')
                
            return redirect('/account')
            
        @app.route('/account/settings', methods=['POST'])
        @login_required
        def update_settings():
            """Update account settings"""
            session_id = request.cookies.get('session_id')
            valid, username = self.auth.verify_session(session_id)
            
            if not valid:
                return redirect('/login')
                
            email = request.form.get('email')
            save_analyses = 'save_analyses' in request.form
            
            # Update user information
            user = self.auth.users.get(username, {})
            user['email'] = email
            user['save_analyses'] = save_analyses
            self.auth._save_users()
            
            flash('Settings updated successfully', 'success')
            return redirect('/account')
            
        @app.route('/account/delete', methods=['POST'])
        @login_required
        def delete_account():
            """Delete account"""
            session_id = request.cookies.get('session_id')
            valid, username = self.auth.verify_session(session_id)
            
            if not valid:
                return redirect('/login')
                
            # Delete user
            success, message = self.auth.delete_user(username)
            
            if success:
                # Remove session cookie
                resp = make_response(redirect('/login'))
                resp.set_cookie('session_id', '', expires=0)
                flash('Your account has been deleted', 'success')
                return resp
            else:
                flash(message, 'error')
                return redirect('/account')
        
        @app.route('/report')
        @login_required
        def report():
            """Serve the HTML report"""
            report_path = os.path.join(self.output_dir, 'report.html')
            if not os.path.exists(report_path):
                flash('No report available. Please upload a Telegram export file.', 'warning')
                return redirect('/upload')
                
            return send_from_directory(self.output_dir, 'report.html')
        
        # Update the static_files route in web_server.py to properly handle visualization files:

        @app.route('/static/<path:filename>')
        def static_files(filename):
            """Serve static files"""
            # First check if it's a direct file in the output directory
            if os.path.exists(os.path.join(self.output_dir, filename)):
                return send_from_directory(self.output_dir, filename)
            
            # Check if it's in the static directory in the package
            package_static_path = os.path.join(os.path.dirname(__file__), 'static')
            if os.path.exists(os.path.join(package_static_path, filename)):
                return send_from_directory(package_static_path, filename)
                
            # Special case for visualization files - they might not have the correct path prefix
            visualization_files = [
                'activity_heatmap.png', 'user_activity.png', 'sentiment_timeline.png',
                'wordcloud.png', 'media_distribution.png', 'weekly_activity.png',
                'message_length_histogram.png', 'response_time_analysis.png',
                'emoji_usage.png', 'user_message_timeline.png', 'topic_clusters.png',
                'user_interaction_network.png', 'word_frequency.png',
                'sentiment_distribution.png', 'conversation_flow.png'
            ]
            
            if filename in visualization_files:
                self.logger.info(f"Visualization file requested: {filename}")
                # Log all files in the output directory for debugging
                try:
                    files_in_output = os.listdir(self.output_dir)
                    self.logger.info(f"Files in output directory: {files_in_output}")
                except Exception as e:
                    self.logger.error(f"Error listing files in output directory: {str(e)}")
                
                return send_from_directory(self.output_dir, filename)
            
            # If file not found in any location, return 404
            self.logger.warning(f"File not found: {filename}")
            return "", 404
        
        @app.route('/online_presence/<path:filename>')
        def serve_online_presence(filename):
            """Serve files from the online_presence subdirectory."""
            online_presence_dir = os.path.join(self.output_dir, 'online_presence')
            return send_from_directory(online_presence_dir, filename)
        
        
        
        # Add a route specifically for visualization files
        @app.route('/<path:filename>.png')
        def visualization_files(filename):
            """Serve visualization PNG files from the output directory"""
            full_filename = f"{filename}.png"
            if os.path.exists(os.path.join(self.output_dir, full_filename)):
                return send_from_directory(self.output_dir, full_filename)
            
            # Log information about the missing file
            self.logger.warning(f"Visualization file not found: {full_filename}")
            return "", 404
        
        
        @app.route('/interactive/<path:filename>')
        @login_required
        def interactive_files(filename):
            """Serve interactive visualization files"""
            interactive_dir = os.path.join(self.output_dir, 'interactive')
            return send_from_directory(interactive_dir, filename)
        
        @app.route('/api/stats')
        @login_required
        def get_stats():
            """API endpoint to get JSON statistics"""
            stats_path = os.path.join(self.output_dir, 'stats.json')
            if os.path.exists(stats_path):
                with open(stats_path, 'r', encoding='utf-8') as f:
                    import json
                    return jsonify(json.load(f))
            else:
                return jsonify({"error": "Statistics not found"})
        
        @app.route('/api/visualizations')
        @login_required
        def get_visualizations():
            """API endpoint to get list of available visualizations"""
            static_viz = []
            interactive_viz = []
            
            # Look for static visualizations
            for file in os.listdir(self.output_dir):
                if file.endswith('.png'):
                    static_viz.append(file)
            
            # Look for interactive visualizations
            interactive_dir = os.path.join(self.output_dir, 'interactive')
            if os.path.exists(interactive_dir):
                for file in os.listdir(interactive_dir):
                    if file.endswith('.html'):
                        interactive_viz.append(file)
            
            return jsonify({
                "static": static_viz,
                "interactive": interactive_viz
            })
        
        @app.route('/upload', methods=['GET', 'POST'])
        @login_required
        def upload_file():
            """Handle file upload and analysis"""
            # Get username for template
            session_id = request.cookies.get('session_id')
            valid, username = self.auth.verify_session(session_id)
            
            if not valid:
                return redirect('/login')
                
            if request.method == 'POST':
                # Check if a file was uploaded
                if 'file' not in request.files:
                    flash('No file part', 'error')
                    return redirect(request.url)
                
                file = request.files['file']
                
                # If the user does not select a file, the browser submits an empty file
                if file.filename == '':
                    flash('No selected file', 'error')
                    return redirect(request.url)
                
                if file:
                    # Check file extension
                    if not file.filename.lower().endswith('.json'):
                        flash('Invalid file format. Please upload a JSON file', 'error')
                        return redirect(request.url)
                        
                    # Save the uploaded file
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    # Start analysis in a background thread
                    session['analysis_running'] = True
                    session['analysis_progress'] = 0
                    threading.Thread(
                        target=self._run_analysis, 
                        args=(file_path, username)
                    ).start()
                    
                    return render_template('analysis.html', filename=filename, username=username)
            
            return render_template('upload.html', username=username)
        
        @app.route('/status')
        @login_required
        def status():
            """Check analysis status"""
            if not session.get('analysis_running', False):
                # Analysis is no longer running
                if os.path.exists(os.path.join(self.output_dir, 'report.html')):
                    # Analysis completed successfully
                    return jsonify({"status": "complete", "redirect": "/report"})
                else:
                    # Analysis failed
                    return jsonify({"status": "failed", "redirect": "/"})
            
            # Analysis is still running
            progress = session.get('analysis_progress', 0)
            
            # Simulate progress for demo purposes
            if progress < 95:
                progress += 5
                session['analysis_progress'] = progress
                
            return jsonify({
                "status": "running", 
                "progress": progress
            })
            
        @app.route('/api/upload-status', methods=['GET'])
        @login_required
        def upload_status():
            """API endpoint to check upload and analysis status"""
            upload_id = request.args.get('id')
            
            # In a real app, you'd store and retrieve actual upload status
            # This is just a placeholder
            return jsonify({
                "status": "processing",
                "progress": 75,
                "message": "Processing messages..."
            })
            
        @app.route('/analyses/<analysis_id>')
        @login_required
        def view_analysis(analysis_id):
            """View a specific analysis"""
            # In a real implementation, you would load the specific analysis
            # For now, just redirect to the report
            return redirect('/report')
            
        @app.route('/analyses/<analysis_id>/delete')
        @login_required
        def delete_analysis(analysis_id):
            """Delete a specific analysis"""
            # In a real implementation, you would delete the specific analysis
            flash('Analysis deleted successfully', 'success')
            return redirect('/account')
        
        # Error handlers
        @app.errorhandler(404)
        def page_not_found(e):
            # Get username if logged in
            username = None
            session_id = request.cookies.get('session_id')
            if session_id:
                valid, username = self.auth.verify_session(session_id)
                if valid:
                    username = username
            
            return render_template('404.html', username=username), 404
            
        @app.errorhandler(413)
        def request_entity_too_large(e):
            flash('File too large (max 50MB)', 'error')
            return redirect('/upload')
        
        # Add templates directory
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        if os.path.exists(template_dir):
            app.template_folder = template_dir
        
        return app
    
    def _run_analysis(self, file_path, username=None):
        """Run analysis in a background thread"""
        try:
            self.logger.info(f"Starting analysis of {file_path}")
            
            # Import analysis modules here to avoid circular imports
            from telegram_analyzer.parser import TelegramDataParser
            from telegram_analyzer.analyzer import ChatAnalyzer
            from telegram_analyzer.visualizer import Visualizer
            from telegram_analyzer.report import ReportGenerator
            from telegram_analyzer.stats_export import export_stats_to_json
            
            # Update progress
            session = {}
            session['analysis_progress'] = 10
            
            # Process messages
            self.logger.info("Processing messages...")
            data_parser = TelegramDataParser(file_path)
            messages_df = data_parser.process_messages()
            self.logger.info(f"Processed {len(messages_df)} messages")
            
            # Update progress
            session['analysis_progress'] = 30

            # Analyze chat
            self.logger.info("Analyzing chat...")
            analyzer = ChatAnalyzer(messages_df)
            analysis_results = analyzer.get_all_stats()
            
            # Update progress
            session['analysis_progress'] = 50
            
            # Export statistics to JSON for web server
            export_stats_to_json(analysis_results, self.output_dir)

            # Generate standard visualizations
            self.logger.info("Generating visualizations...")
            visualizer = Visualizer(messages_df, self.output_dir)
            generated_viz = visualizer.generate_all_visualizations()
            self.logger.info(f"Generated {len(generated_viz)} static visualizations")
            
            # Update progress
            session['analysis_progress'] = 70
            
            # Generate interactive visualizations if available
            interactive_viz = []
            try:
                from telegram_analyzer.enhanced_visualizer import EnhancedVisualizer
                self.logger.info("Generating interactive visualizations...")
                enhanced_viz = EnhancedVisualizer(messages_df, self.output_dir)
                interactive_viz = enhanced_viz.generate_all_visualizations()
                self.logger.info(f"Generated {len(interactive_viz)} interactive visualizations")
            except ImportError:
                self.logger.info("Enhanced visualization module not available. Skipping interactive visualizations.")

            # Update progress
            session['analysis_progress'] = 90
            
            # Generate report
            self.logger.info("Generating report...")
            report_generator = ReportGenerator(analysis_results, self.output_dir)
            report_generator.generate_html_report(interactive_viz)

            self.logger.info(f"Analysis complete! Report saved to {self.output_dir}/report.html")
            
            # If user is authenticated and enabled saving analyses, save the analysis
            if username:
                user = self.auth.users.get(username, {})
                if user.get('save_analyses', True):
                    # In a real implementation, you would save the analysis to a database
                    # For now, just log it
                    self.logger.info(f"Saving analysis for user {username}")
            
            # Update progress
            session['analysis_progress'] = 100
            session['analysis_running'] = False
            
        except Exception as e:
            self.logger.error(f"Error during analysis: {str(e)}", exc_info=True)
            session = {}
            session['analysis_running'] = False
        
        finally:
            # Clean up uploaded file
            try:
                os.remove(file_path)
            except:
                pass
        
    def run(self):
        """Run the web server"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            self.logger.info(f"Created output directory: {self.output_dir}")
            
        self.logger.info(f"Starting web server at http://{self.host}:{self.port}")
        self.logger.info("Authentication is required for all users")
        
        # Open browser in a separate thread
        if self.open_browser:
            threading.Thread(target=self._open_browser_delayed).start()
        
        # Run Flask app
        self.app.run(host=self.host, port=self.port, debug=False)
        return True
        
    def _open_browser_delayed(self):
        """Open browser after a short delay to allow server to start"""
        time.sleep(1.5)  # Wait for server to start
        webbrowser.open(f"http://{self.host}:{self.port}")

def create_server(output_dir, host='127.0.0.1', port=5000, open_browser=True, 
                 user_db_path=None, enable_auth=True):
    """
    Create and return a web server instance.
    
    Args:
        output_dir: Directory containing analysis results
        host: Host to run the server on
        port: Port to run the server on
        open_browser: Whether to automatically open the browser
        user_db_path: Path to user database file
        enable_auth: Whether to enable authentication (ignored, always enabled)
        
    Returns:
        AnalyzerWebServer instance
    """
    try:
        return AnalyzerWebServer(output_dir, host, port, open_browser, user_db_path, True)
    except ImportError as e:
        logging.error(f"Failed to create web server: {str(e)}")
        return None

def run_server(output_dir, host='127.0.0.1', port=5000, open_browser=True, 
              user_db_path=None, enable_auth=True):
    """
    Create and run a web server.
    
    Args:
        output_dir: Directory containing analysis results
        host: Host to run the server on
        port: Port to run the server on
        open_browser: Whether to automatically open the browser
        user_db_path: Path to user database file
        enable_auth: Whether to enable authentication (ignored, always enabled)
        
    Returns:
        True if server was started successfully, False otherwise
    """
    server = create_server(output_dir, host, port, open_browser, user_db_path, True)
    if server:
        return server.run()
    return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Telegram Analyzer web server")
    parser.add_argument("output_dir", help="Directory containing analysis results")
    parser.add_argument("--host", default="127.0.0.1", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the server on")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    parser.add_argument("--user-db", default="users.json", help="Path to user database file")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    run_server(
        args.output_dir, 
        args.host, 
        args.port, 
        not args.no_browser,
        args.user_db,
        True  # Authentication is always enabled
    )