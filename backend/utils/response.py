"""
response.py — Standardized JSON response helpers

Semua API endpoint menggunakan format response yang konsisten:
- Success: {"success": true, "data": {...}, "message": "..."}
- Error:   {"success": false, "error": "...", "code": 400}
"""

from flask import jsonify


def success_response(data=None, message="Operation successful", status_code=200):
    """
    Buat response JSON untuk operasi yang berhasil.
    
    Args:
        data (dict, optional): Data hasil operasi (statistik, URL download, dll)
        message (str): Pesan deskriptif
        status_code (int): HTTP status code (default 200)
    
    Returns:
        Flask Response dengan format JSON standar
    """
    response = {
        "success": True,
        "message": message,
        "data": data or {}
    }
    return jsonify(response), status_code


def error_response(message="An error occurred", status_code=400, details=None):
    """
    Buat response JSON untuk operasi yang gagal.
    
    Args:
        message (str): Pesan error yang user-friendly
        status_code (int): HTTP status code (400, 404, 413, 500, dll)
        details (str, optional): Detail teknis tambahan untuk debugging
    
    Returns:
        Flask Response dengan format JSON standar
    """
    response = {
        "success": False,
        "error": message,
        "code": status_code
    }
    if details:
        response["details"] = details
    return jsonify(response), status_code
