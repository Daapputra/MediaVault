"""
compression_routes.py — REST API endpoints untuk kompresi dan dekompresi

Endpoints:
  POST /api/compress/image     — Kompresi image
  POST /api/decompress/image   — Dekompresi image (.mvault → image)
  POST /api/compress/audio     — Kompresi audio (Phase 2)
  POST /api/decompress/audio   — Dekompresi audio (Phase 2)
  POST /api/compress/video     — Kompresi video (Phase 3)
  POST /api/decompress/video   — Dekompresi video (Phase 3)
  GET  /api/download/<filename> — Download file hasil
"""

import os
from flask import Blueprint, request, send_file

from utils.response import success_response, error_response
from utils.file_handler import validate_file, save_upload, get_file_size, format_file_size, cleanup_file
from config import OUTPUT_FOLDER

# Blueprint untuk semua route kompresi
compression_bp = Blueprint('compression', __name__, url_prefix='/api')


@compression_bp.route('/compress/image', methods=['POST'])
def compress_image():
    """
    Kompresi image file.
    
    Input: FormData dengan field 'file' (image: PNG, BMP, JPG, TIFF)
    Output: JSON dengan statistik dan URL download
    """
    # Cek apakah ada file di request
    if 'file' not in request.files:
        return error_response("No file provided. Please upload an image file.", 400)
    
    file = request.files['file']
    
    # Validasi file
    is_valid, error_msg = validate_file(file, 'image')
    if not is_valid:
        return error_response(error_msg, 400)
    
    input_path = None
    try:
        # Simpan file upload
        input_path, original_filename = save_upload(file, 'input')
        
        # Kompresi
        from modules.compression.image_codec import compress_image as do_compress
        result = do_compress(input_path)
        
        # Ambil nama file output untuk download URL
        output_filename = os.path.basename(result['output_path'])
        
        return success_response(
            data={
                'original_filename': original_filename,
                'original_size': result['original_size'],
                'original_size_formatted': format_file_size(result['original_size']),
                'original_raw_size': result['original_raw_size'],
                'original_raw_size_formatted': format_file_size(result['original_raw_size']),
                'compressed_size': result['compressed_size'],
                'compressed_size_formatted': format_file_size(result['compressed_size']),
                'compression_ratio': result['compression_ratio'],
                'processing_time': result['processing_time'],
                'width': result['width'],
                'height': result['height'],
                'mode': result['mode'],
                'download_url': f'/api/download/{output_filename}'
            },
            message="Image compressed successfully"
        )
    
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Compression failed: {str(e)}", 500)
    finally:
        # Cleanup input file
        cleanup_file(input_path)


@compression_bp.route('/decompress/image', methods=['POST'])
def decompress_image():
    """
    Dekompresi file .mvault kembali menjadi image.
    
    Input: FormData dengan field 'file' (file .mvault)
    Output: JSON dengan statistik dan URL download
    """
    if 'file' not in request.files:
        return error_response("No file provided. Please upload a .mvault file.", 400)
    
    file = request.files['file']
    
    # Validasi — izinkan file .mvault
    is_valid, error_msg = validate_file(file, 'image', allow_compressed=True)
    if not is_valid:
        return error_response(error_msg, 400)
    
    input_path = None
    try:
        input_path, original_filename = save_upload(file, 'input')
        
        from modules.compression.image_codec import decompress_image as do_decompress
        result = do_decompress(input_path)
        
        output_filename = os.path.basename(result['output_path'])
        
        return success_response(
            data={
                'original_filename': original_filename,
                'compressed_size': result['compressed_size'],
                'compressed_size_formatted': format_file_size(result['compressed_size']),
                'decompressed_size': result['decompressed_size'],
                'decompressed_size_formatted': format_file_size(result['decompressed_size']),
                'processing_time': result['processing_time'],
                'width': result['width'],
                'height': result['height'],
                'mode': result['mode'],
                'download_url': f'/api/download/{output_filename}'
            },
            message="Image decompressed successfully"
        )
    
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Decompression failed: {str(e)}", 500)
    finally:
        cleanup_file(input_path)


@compression_bp.route('/compress/audio', methods=['POST'])
def compress_audio():
    """Kompresi audio — akan diimplementasi di Phase 2."""
    return error_response("Audio compression coming soon (Phase 2)", 501)


@compression_bp.route('/decompress/audio', methods=['POST'])
def decompress_audio():
    """Dekompresi audio — akan diimplementasi di Phase 2."""
    return error_response("Audio decompression coming soon (Phase 2)", 501)


@compression_bp.route('/compress/video', methods=['POST'])
def compress_video():
    """Kompresi video — akan diimplementasi di Phase 3."""
    return error_response("Video compression coming soon (Phase 3)", 501)


@compression_bp.route('/decompress/video', methods=['POST'])
def decompress_video():
    """Dekompresi video — akan diimplementasi di Phase 3."""
    return error_response("Video decompression coming soon (Phase 3)", 501)


@compression_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """
    Download file hasil proses (kompresi, dekompresi, atau steganografi).
    
    Args:
        filename: Nama file di folder output
    
    Returns:
        File download response
    """
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    
    if not os.path.exists(file_path):
        return error_response("File not found. It may have been cleaned up.", 404)
    
    # Tentukan MIME type berdasarkan ekstensi
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    mime_types = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'bmp': 'image/bmp',
        'wav': 'audio/wav',
        'avi': 'video/x-msvideo',
        'mp4': 'video/mp4',
        'mvault': 'application/octet-stream'
    }
    mimetype = mime_types.get(ext, 'application/octet-stream')
    
    return send_file(
        file_path,
        mimetype=mimetype,
        as_attachment=True,
        download_name=filename
    )
