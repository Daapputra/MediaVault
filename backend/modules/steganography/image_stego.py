"""
image_stego.py — Steganografi Image menggunakan LSB

Menyembunyikan pesan teks di dalam image dengan memodifikasi
Least Significant Bit (LSB) dari setiap komponen warna pixel.

Alur Embed:
1. Baca image dengan Pillow
2. Flatten pixel data menjadi array 1D
3. Cek kapasitas (jumlah pixel × channels harus cukup untuk pesan)
4. Embed pesan menggunakan LSB
5. Rekonstruksi image dari pixel data yang sudah dimodifikasi
6. Simpan sebagai PNG (WAJIB lossless, JPG akan rusak!)

Alur Extract:
1. Baca stego image
2. Flatten pixel data
3. Baca LSB untuk extract pesan
4. Return pesan

PENTING: Output HARUS PNG (lossless). Jika disimpan sebagai JPG,
kompresi lossy akan merusak LSB dan pesan tidak bisa diekstrak!
"""

import os
import time
from PIL import Image

from modules.steganography.lsb import embed, extract, calculate_capacity


def embed_message(image_path, message):
    """
    Sisipkan pesan tersembunyi ke dalam image menggunakan LSB.
    
    Args:
        image_path (str): Path ke image carrier (PNG, BMP, dll)
        message (str): Pesan yang akan disembunyikan
    
    Returns:
        dict: {
            'output_path': path ke stego image (PNG),
            'original_size': ukuran image asli (bytes),
            'stego_size': ukuran stego image (bytes),
            'message_length': panjang pesan (karakter),
            'capacity': kapasitas maksimum carrier (karakter),
            'processing_time': waktu proses (detik)
        }
    
    Raises:
        ValueError: Jika pesan terlalu panjang atau image tidak bisa dibuka
    """
    start_time = time.time()
    
    # ── Langkah 1: Baca image ──
    try:
        img = Image.open(image_path)
    except Exception as e:
        raise ValueError(f"Cannot open image file: {str(e)}")
    
    # Konversi ke RGB jika perlu (misal JPEG yang mode-nya bisa macam-macam)
    # Kita pakai RGB supaya konsisten (3 channel per pixel)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')
    
    width, height = img.size
    mode = img.mode
    
    # ── Langkah 2: Flatten pixel data ke bytearray ──
    # Image RGB 100x100 → 30000 bytes (100 × 100 × 3 channels)
    pixel_data = bytearray(img.tobytes())
    
    # ── Langkah 3: Cek kapasitas ──
    capacity = calculate_capacity(pixel_data)
    message_bytes_len = len(message.encode('utf-8'))
    
    if message_bytes_len > capacity:
        raise ValueError(
            f"Message too long! Your message is {message_bytes_len} bytes, "
            f"but this image can only hide {capacity} bytes. "
            f"Use a larger image or a shorter message."
        )
    
    # ── Langkah 4: Embed pesan ──
    stego_data = embed(pixel_data, message)
    
    # ── Langkah 5: Rekonstruksi image ──
    stego_img = Image.frombytes(mode, (width, height), bytes(stego_data))
    
    # Simpan sebagai PNG (WAJIB lossless!)
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_path = os.path.join(
        os.path.dirname(image_path).replace('input', 'output'),
        f"{base_name}_stego.png"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    stego_img.save(output_path, format='PNG')
    
    # ── Kalkulasi statistik ──
    processing_time = time.time() - start_time
    original_size = os.path.getsize(image_path)
    stego_size = os.path.getsize(output_path)
    
    return {
        'output_path': output_path,
        'original_size': original_size,
        'stego_size': stego_size,
        'message_length': message_bytes_len,
        'capacity': capacity,
        'usage_percent': round((message_bytes_len / capacity) * 100, 2) if capacity > 0 else 0,
        'processing_time': round(processing_time, 3),
        'width': width,
        'height': height
    }


def extract_message(image_path):
    """
    Ekstrak pesan tersembunyi dari stego image.
    
    Args:
        image_path (str): Path ke stego image (harus PNG atau format lossless)
    
    Returns:
        dict: {
            'message': pesan yang berhasil diekstrak,
            'message_length': panjang pesan (karakter),
            'processing_time': waktu proses (detik)
        }
    
    Raises:
        ValueError: Jika tidak ada pesan tersembunyi yang valid
    """
    start_time = time.time()
    
    # ── Langkah 1: Baca image ──
    try:
        img = Image.open(image_path)
    except Exception as e:
        raise ValueError(f"Cannot open image file: {str(e)}")
    
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')
    
    # ── Langkah 2: Flatten pixel data ──
    pixel_data = bytearray(img.tobytes())
    
    # ── Langkah 3: Extract pesan ──
    message = extract(pixel_data)
    
    processing_time = time.time() - start_time
    
    return {
        'message': message,
        'message_length': len(message),
        'processing_time': round(processing_time, 3)
    }
