"""
steganography_routes.py — REST API endpoints untuk steganografi

Endpoints:
  POST /api/stego/image/embed    — Sisipkan pesan ke image
  POST /api/stego/image/extract  — Ekstrak pesan dari image
  POST /api/stego/audio/embed    — Sisipkan pesan ke audio (Phase 2)
  POST /api/stego/audio/extract  — Ekstrak pesan dari audio (Phase 2)
  POST /api/stego/video/embed    — Sisipkan pesan ke video (Phase 3)
  POST /api/stego/video/extract  — Ekstrak pesan dari video (Phase 3)
"""

import os
from flask import Blueprint, request

from utils.response import success_response, error_response
from utils.file_handler import validate_file, save_upload, format_file_size, cleanup_file

# Blueprint untuk semua route steganografi
steganography_bp = Blueprint('steganography', __name__, url_prefix='/api/stego')


@steganography_bp.route('/image/embed', methods=['POST'])
def embed_image():
    """
    Sisipkan pesan tersembunyi ke dalam image.
    
    Input: FormData dengan:
      - 'file': image file (PNG, BMP — sebaiknya lossless)
      - 'message': pesan teks yang akan disembunyikan
    
    Output: JSON dengan statistik dan URL download stego image
    """
    # Validasi input
    if 'file' not in request.files:
        return error_response("No image file provided.", 400)
    
    message = request.form.get('message', '').strip()
    if not message:
        return error_response("No message provided. Please enter a message to hide.", 400)
    
    file = request.files['file']
    
    is_valid, error_msg = validate_file(file, 'image')
    if not is_valid:
        return error_response(error_msg, 400)
    
    input_path = None
    try:
        input_path, original_filename = save_upload(file, 'input')
        
        from modules.steganography.image_stego import embed_message
        result = embed_message(input_path, message)
        
        output_filename = os.path.basename(result['output_path'])
        
        return success_response(
            data={
                'original_filename': original_filename,
                'original_size': result['original_size'],
                'original_size_formatted': format_file_size(result['original_size']),
                'stego_size': result['stego_size'],
                'stego_size_formatted': format_file_size(result['stego_size']),
                'message_length': result['message_length'],
                'capacity': result['capacity'],
                'usage_percent': result['usage_percent'],
                'processing_time': result['processing_time'],
                'width': result['width'],
                'height': result['height'],
                'download_url': f'/api/download/{output_filename}'
            },
            message="Message embedded successfully"
        )
    
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Embedding failed: {str(e)}", 500)
    finally:
        cleanup_file(input_path)


@steganography_bp.route('/image/extract', methods=['POST'])
def extract_image():
    """
    Ekstrak pesan tersembunyi dari stego image.
    
    Input: FormData dengan field 'file' (stego image, harus PNG)
    Output: JSON dengan pesan yang diekstrak
    """
    if 'file' not in request.files:
        return error_response("No image file provided.", 400)
    
    file = request.files['file']
    
    is_valid, error_msg = validate_file(file, 'image')
    if not is_valid:
        return error_response(error_msg, 400)
    
    input_path = None
    try:
        input_path, original_filename = save_upload(file, 'input')
        
        from modules.steganography.image_stego import extract_message
        result = extract_message(input_path)
        
        return success_response(
            data={
                'original_filename': original_filename,
                'message': result['message'],
                'message_length': result['message_length'],
                'processing_time': result['processing_time']
            },
            message="Message extracted successfully"
        )
    
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Extraction failed: {str(e)}", 500)
    finally:
        cleanup_file(input_path)


@steganography_bp.route('/audio/embed', methods=['POST'])
def embed_audio():
    if 'file' not in request.files:
        return error_response("No audio file provided.", 400)
    
    message = request.form.get('message', '').strip()
    if not message:
        return error_response("No message provided. Please enter a message to hide.", 400)
    
    file = request.files['file']
    is_valid, error_msg = validate_file(file, 'audio')
    if not is_valid:
        return error_response(error_msg, 400)
    
    input_path = None
    try:
        input_path, original_filename = save_upload(file, 'input')
        
        from modules.steganography.audio_stego import embed_message
        result = embed_message(input_path, message)
        
        output_filename = os.path.basename(result['output_path'])
        
        return success_response(
            data={
                'original_filename': original_filename,
                'original_size': result['original_size'],
                'original_size_formatted': format_file_size(result['original_size']),
                'stego_size': result['stego_size'],
                'stego_size_formatted': format_file_size(result['stego_size']),
                'message_length': result['message_length'],
                'capacity': result['capacity'],
                'usage_percent': result['usage_percent'],
                'processing_time': result['processing_time'],
                'download_url': f'/api/download/{output_filename}'
            },
            message="Message embedded successfully"
        )
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Embedding failed: {str(e)}", 500)
    finally:
        cleanup_file(input_path)


@steganography_bp.route('/audio/extract', methods=['POST'])
def extract_audio():
    if 'file' not in request.files:
        return error_response("No audio file provided.", 400)
    
    file = request.files['file']
    is_valid, error_msg = validate_file(file, 'audio')
    if not is_valid:
        return error_response(error_msg, 400)
    
    input_path = None
    try:
        input_path, original_filename = save_upload(file, 'input')
        
        from modules.steganography.audio_stego import extract_message
        result = extract_message(input_path)
        
        return success_response(
            data={
                'original_filename': original_filename,
                'message': result['message'],
                'message_length': result['message_length'],
                'processing_time': result['processing_time']
            },
            message="Message extracted successfully"
        )
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Extraction failed: {str(e)}", 500)
    finally:
        cleanup_file(input_path)


@steganography_bp.route('/video/embed', methods=['POST'])
def embed_video():
    if 'file' not in request.files:
        return error_response("No video file provided.", 400)
    
    message = request.form.get('message', '').strip()
    if not message:
        return error_response("No message provided. Please enter a message to hide.", 400)
    
    file = request.files['file']
    is_valid, error_msg = validate_file(file, 'video')
    if not is_valid:
        return error_response(error_msg, 400)
    
    input_path = None
    try:
        input_path, original_filename = save_upload(file, 'input')
        
        from modules.steganography.video_stego import embed_message
        result = embed_message(input_path, message)
        
        output_filename = os.path.basename(result['output_path'])
        
        return success_response(
            data={
                'original_filename': original_filename,
                'original_size': result['original_size'],
                'original_size_formatted': format_file_size(result['original_size']),
                'stego_size': result['stego_size'],
                'stego_size_formatted': format_file_size(result['stego_size']),
                'message_length': result['message_length'],
                'capacity': result['capacity'],
                'usage_percent': result['usage_percent'],
                'processing_time': result['processing_time'],
                'download_url': f'/api/download/{output_filename}'
            },
            message="Message embedded successfully"
        )
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Embedding failed: {str(e)}", 500)
    finally:
        cleanup_file(input_path)


@steganography_bp.route('/video/extract', methods=['POST'])
def extract_video():
    if 'file' not in request.files:
        return error_response("No video file provided.", 400)
    
    file = request.files['file']
    is_valid, error_msg = validate_file(file, 'video')
    if not is_valid:
        return error_response(error_msg, 400)
    
    input_path = None
    try:
        input_path, original_filename = save_upload(file, 'input')
        
        from modules.steganography.video_stego import extract_message
        result = extract_message(input_path)
        
        return success_response(
            data={
                'original_filename': original_filename,
                'message': result['message'],
                'message_length': result['message_length'],
                'processing_time': result['processing_time']
            },
            message="Message extracted successfully"
        )
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Extraction failed: {str(e)}", 500)
    finally:
        cleanup_file(input_path)

