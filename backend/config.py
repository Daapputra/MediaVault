"""
config.py — Konfigurasi aplikasi Media Vault

Berisi semua pengaturan untuk Flask app:
- Path untuk upload/output files
- Batas ukuran file per media type
- Ekstensi file yang diizinkan
"""

import os

# Base directory (folder backend/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Upload & Output Directories ────────────────────────────────────
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'input')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'uploads', 'output')

# Buat folder jika belum ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ─── File Size Limits (bytes) ───────────────────────────────────────
MAX_IMAGE_SIZE = 20 * 1024 * 1024   # 20 MB
MAX_AUDIO_SIZE = 30 * 1024 * 1024   # 30 MB
MAX_VIDEO_SIZE = 50 * 1024 * 1024   # 50 MB
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB (Flask global limit)

# ─── Allowed File Extensions ────────────────────────────────────────
ALLOWED_IMAGE_EXTENSIONS = {'png', 'bmp', 'jpg', 'jpeg', 'tiff'}
ALLOWED_AUDIO_EXTENSIONS = {'wav'}
ALLOWED_VIDEO_EXTENSIONS = {'avi', 'mp4'}

# Ekstensi untuk file hasil kompresi Media Vault
COMPRESSED_EXTENSION = '.mvault'

# ─── Video Processing Limits ────────────────────────────────────────
MAX_VIDEO_FRAMES = 30       # Batasi max 30 frames untuk demo
MAX_VIDEO_DURATION = 10     # Max 10 detik

# ─── Steganography ──────────────────────────────────────────────────
STEGO_DELIMITER = '###END###'  # Penanda akhir pesan tersembunyi
