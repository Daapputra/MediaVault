"""
file_handler.py — Utilitas pengelolaan file

Menangani:
- Validasi file upload (format, ukuran, corruption check)
- Penyimpanan file sementara dengan nama unik
- Pembersihan file temporary
- Kalkulasi ukuran file
"""

import os
import uuid
import hashlib
from werkzeug.utils import secure_filename

from config import (
    UPLOAD_FOLDER, OUTPUT_FOLDER,
    ALLOWED_IMAGE_EXTENSIONS, ALLOWED_AUDIO_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS,
    MAX_IMAGE_SIZE, MAX_AUDIO_SIZE, MAX_VIDEO_SIZE, COMPRESSED_EXTENSION
)


def get_allowed_extensions(media_type):
    """
    Ambil set ekstensi file yang diizinkan berdasarkan tipe media.
    
    Args:
        media_type (str): 'image', 'audio', atau 'video'
    
    Returns:
        set: Ekstensi yang diizinkan (e.g., {'png', 'bmp', 'jpg'})
    """
    mapping = {
        'image': ALLOWED_IMAGE_EXTENSIONS,
        'audio': ALLOWED_AUDIO_EXTENSIONS,
        'video': ALLOWED_VIDEO_EXTENSIONS,
    }
    return mapping.get(media_type, set())


def get_max_size(media_type):
    """Ambil batas ukuran file berdasarkan tipe media."""
    mapping = {
        'image': MAX_IMAGE_SIZE,
        'audio': MAX_AUDIO_SIZE,
        'video': MAX_VIDEO_SIZE,
    }
    return mapping.get(media_type, MAX_IMAGE_SIZE)


def get_file_extension(filename):
    """Ambil ekstensi file (lowercase, tanpa titik)."""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def validate_file(file, media_type, allow_compressed=False):
    """
    Validasi file upload: cek nama, ekstensi, dan ukuran.
    
    Args:
        file: FileStorage object dari Flask request
        media_type (str): 'image', 'audio', atau 'video'
        allow_compressed (bool): Jika True, izinkan file .mvault (untuk dekompresi)
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    # Cek apakah file ada dan punya nama
    if file is None or file.filename == '':
        return False, "No file provided or filename is empty"
    
    filename = file.filename
    ext = get_file_extension(filename)
    
    # Cek ekstensi
    allowed = get_allowed_extensions(media_type)
    if allow_compressed:
        # Untuk dekompresi, terima file .mvault
        if ext != 'mvault' and ext not in allowed:
            return False, f"Unsupported file format '.{ext}'. Allowed: {', '.join(allowed)} or .mvault"
    else:
        if ext not in allowed:
            return False, f"Unsupported file format '.{ext}'. Allowed: {', '.join(allowed)}"
    
    # Cek ukuran file (seek ke akhir untuk hitung size)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset posisi ke awal
    
    if file_size == 0:
        return False, "File is empty (0 bytes)"
    
    max_size = get_max_size(media_type)
    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        file_mb = file_size / (1024 * 1024)
        return False, f"File too large ({file_mb:.1f} MB). Maximum allowed: {max_mb:.0f} MB"
    
    return True, None


def save_upload(file, subfolder='input'):
    """
    Simpan file upload ke folder sementara dengan nama unik.
    
    Args:
        file: FileStorage object dari Flask request
        subfolder (str): 'input' atau 'output'
    
    Returns:
        tuple: (saved_path: str, original_filename: str)
    """
    folder = UPLOAD_FOLDER if subfolder == 'input' else OUTPUT_FOLDER
    os.makedirs(folder, exist_ok=True)
    
    # Generate nama unik: uuid + ekstensi asli
    original_filename = secure_filename(file.filename)
    ext = get_file_extension(original_filename)
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    
    saved_path = os.path.join(folder, unique_name)
    file.save(saved_path)
    
    return saved_path, original_filename


def save_output(data, filename, extension=None):
    """
    Simpan data hasil proses ke folder output.
    
    Args:
        data (bytes): Data yang akan disimpan
        filename (str): Nama file dasar (tanpa path)
        extension (str, optional): Ekstensi baru (e.g., 'mvault')
    
    Returns:
        str: Path lengkap ke file yang disimpan
    """
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    if extension:
        base = filename.rsplit('.', 1)[0] if '.' in filename else filename
        filename = f"{base}.{extension}"
    
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    output_path = os.path.join(OUTPUT_FOLDER, unique_name)
    
    with open(output_path, 'wb') as f:
        f.write(data)
    
    return output_path


def get_file_size(filepath):
    """
    Hitung ukuran file dalam bytes.
    
    Args:
        filepath (str): Path ke file
    
    Returns:
        int: Ukuran file dalam bytes
    """
    return os.path.getsize(filepath)


def get_file_hash(filepath):
    """
    Hitung SHA-256 hash dari file (untuk verifikasi lossless).
    
    Args:
        filepath (str): Path ke file
    
    Returns:
        str: Hex digest dari SHA-256 hash
    """
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def format_file_size(size_bytes):
    """
    Format ukuran file ke string yang mudah dibaca.
    
    Args:
        size_bytes (int): Ukuran dalam bytes
    
    Returns:
        str: e.g., "1.5 MB", "256 KB", "512 B"
    """
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes} B"


def cleanup_file(filepath):
    """Hapus file sementara jika ada."""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
    except OSError:
        pass  # Ignore cleanup errors
