import os
from flask import Flask, send_from_directory
from flask_cors import CORS


def create_app():
    # Get frontend build directory
    frontend_dist = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
    
    # Don't use Flask's static file handling - we'll handle it manually
    app = Flask(__name__)
    app.config.from_object("config.Config")
    CORS(app)

    # Only register API blueprint - React handles all UI routes
    from app.api import api
    app.register_blueprint(api)

    # Serve React app for all non-API routes
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_react(path):
        # Skip API routes - let API blueprint handle them
        if path.startswith("api/"):
            return "", 404
        
        # Serve static files if they exist (assets, etc.)
        if path and os.path.exists(os.path.join(frontend_dist, path)):
            return send_from_directory(frontend_dist, path)
        
        # Fallback to index.html for SPA routing
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(frontend_dist, "index.html")
        
        return "Frontend not built. Run 'npm run build' in frontend directory.", 503

    return app