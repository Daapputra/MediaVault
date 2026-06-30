"""
app.py — Entry point untuk Media Vault Backend

Flask REST API yang menangani:
- Kompresi/dekompresi image, audio, video
- Steganografi (embed/extract pesan tersembunyi)
- File upload dan download

Jalankan dengan:
  cd backend
  pip install -r requirements.txt
  python app.py
  
Server akan berjalan di http://localhost:5000
"""

import os
import sys

# Tambahkan backend/ ke sys.path agar import modules bisa langsung
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS

from config import MAX_CONTENT_LENGTH
from routes.compression_routes import compression_bp
from routes.steganography_routes import steganography_bp
from utils.response import error_response


def create_app():
    """
    Application factory — buat dan konfigurasi Flask app.
    
    Menggunakan pattern ini agar app bisa di-test dengan mudah
    dan konfigurasi bisa di-override saat testing.
    """
    app = Flask(__name__)
    
    # ── Konfigurasi ──
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    
    # ── CORS — izinkan frontend React (port 5173) mengakses API ──
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # ── Register Blueprints (route groups) ──
    app.register_blueprint(compression_bp)
    app.register_blueprint(steganography_bp)
    
    # ── Health Check Endpoint ──
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Endpoint untuk cek apakah backend berjalan."""
        from utils.response import success_response
        return success_response(
            data={'status': 'healthy', 'version': '1.0.0'},
            message="Media Vault API is running"
        )
    
    # ── Global Error Handlers ──
    @app.errorhandler(404)
    def not_found(e):
        return error_response("Endpoint not found", 404)
    
    @app.errorhandler(413)
    def too_large(e):
        return error_response(
            f"File too large. Maximum upload size is {MAX_CONTENT_LENGTH // (1024*1024)} MB",
            413
        )
    
    @app.errorhandler(500)
    def internal_error(e):
        return error_response("Internal server error. Please try again.", 500)
    
    return app


# ── Entry Point ──
if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*50)
    print("  [SECURE] Media Vault API Server")
    print("  Running on http://localhost:5000")
    print("  Press Ctrl+C to stop")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)
