"""
Main Flask application initialization
"""

from flask import Flask
from flask_cors import CORS
from flask import request, jsonify
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app() -> Flask:
    """
    Create and configure the Flask application
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app)
    
    # Register blueprints
    from api.endpoints import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)