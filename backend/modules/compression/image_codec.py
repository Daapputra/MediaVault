"""
image_codec.py — Kompresi dan Dekompresi Image

Menggunakan Huffman Coding untuk mengkompresi raw pixel data dari image.

Alur kompresi:
1. Baca image dengan Pillow → ambil raw pixel data (bytes)
2. Simpan metadata image (width, height, mode) di header
3. Huffman encode pixel data
4. Output: file .mvault

Alur dekompresi:
1. Baca file .mvault → extract header metadata
2. Huffman decode pixel data
3. Rekonstruksi image dengan Pillow menggunakan metadata
4. Output: file image (PNG — lossless)

LOSSLESS: pixel data hasil dekompresi HARUS identik dengan data asli.
"""

import os
import struct
import time
from PIL import Image

from modules.compression.huffman import encode as huffman_encode, decode as huffman_decode


# Format header file .mvault untuk image:
# ┌──────────────────────────────────────────────┐
# │ Magic: "IMVT" (4 bytes)                      │ ← Image Media Vault
# │ Mode length (1 byte)                         │ ← Panjang string mode
# │ Mode string (N bytes)                        │ ← e.g., "RGB", "RGBA", "L"
# │ Width (4 bytes, big-endian)                  │
# │ Height (4 bytes, big-endian)                 │
# │ Huffman-encoded pixel data                   │
# └──────────────────────────────────────────────┘

IMAGE_MAGIC = b'IMVT'


def compress_image(input_path):
    """
    Kompresi image file menggunakan Huffman Coding.
    
    Args:
        input_path (str): Path ke file image asli (PNG, BMP, JPG, dll)
    
    Returns:
        dict: {
            'output_path': path ke file .mvault,
            'original_size': ukuran file asli (bytes),
            'compressed_size': ukuran file hasil (bytes),
            'compression_ratio': persentase pengurangan ukuran,
            'processing_time': waktu proses (detik),
            'width': lebar image,
            'height': tinggi image,
            'mode': mode warna image
        }
    
    Raises:
        ValueError: Jika file tidak bisa dibaca sebagai image
    """
    start_time = time.time()
    
    # ── Langkah 1: Baca image dan ambil pixel data ──
    try:
        img = Image.open(input_path)
    except Exception as e:
        raise ValueError(f"Cannot open image file: {str(e)}")
    
    width, height = img.size
    mode = img.mode  # "RGB", "RGBA", "L" (grayscale), dll
    
    # Ambil raw pixel data sebagai bytes
    # Contoh: image 2x2 RGB → 12 bytes (2×2×3 channels)
    pixel_data = img.tobytes()
    
    # ── Langkah 2: Bangun header ──
    header = bytearray()
    header.extend(IMAGE_MAGIC)                          # Magic number
    
    mode_bytes = mode.encode('ascii')
    header.append(len(mode_bytes))                      # Mode length
    header.extend(mode_bytes)                           # Mode string
    
    header.extend(struct.pack('>I', width))             # Width
    header.extend(struct.pack('>I', height))            # Height
    
    # ── Langkah 3: Huffman encode pixel data ──
    compressed_pixels = huffman_encode(pixel_data)
    
    # ── Langkah 4: Gabungkan header + compressed data ──
    output_data = bytes(header) + compressed_pixels
    
    # Simpan ke file .mvault
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(
        os.path.dirname(input_path).replace('input', 'output'),
        f"{base_name}_compressed.mvault"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'wb') as f:
        f.write(output_data)
    
    # ── Kalkulasi statistik ──
    processing_time = time.time() - start_time
    original_size = os.path.getsize(input_path)
    compressed_size = len(output_data)
    compression_ratio = (1 - compressed_size / len(pixel_data)) * 100 if len(pixel_data) > 0 else 0
    
    return {
        'output_path': output_path,
        'original_size': original_size,
        'original_raw_size': len(pixel_data),
        'compressed_size': compressed_size,
        'compression_ratio': round(compression_ratio, 2),
        'processing_time': round(processing_time, 3),
        'width': width,
        'height': height,
        'mode': mode
    }


def decompress_image(input_path):
    """
    Dekompresi file .mvault kembali menjadi image.
    
    Args:
        input_path (str): Path ke file .mvault
    
    Returns:
        dict: {
            'output_path': path ke file image hasil (PNG),
            'compressed_size': ukuran file .mvault (bytes),
            'decompressed_size': ukuran file image hasil (bytes),
            'processing_time': waktu proses (detik),
            'width': lebar image,
            'height': tinggi image,
            'mode': mode warna image
        }
    
    Raises:
        ValueError: Jika file .mvault tidak valid
    """
    start_time = time.time()
    
    # Baca file .mvault
    with open(input_path, 'rb') as f:
        data = f.read()
    
    pos = 0
    
    # ── Langkah 1: Baca header ──
    # Magic number
    magic = data[pos:pos+4]
    pos += 4
    if magic != IMAGE_MAGIC:
        raise ValueError(f"Invalid image vault file. Expected 'IMVT' header, got '{magic}'")
    
    # Mode
    mode_length = data[pos]
    pos += 1
    mode = data[pos:pos+mode_length].decode('ascii')
    pos += mode_length
    
    # Dimensions
    width = struct.unpack('>I', data[pos:pos+4])[0]
    pos += 4
    height = struct.unpack('>I', data[pos:pos+4])[0]
    pos += 4
    
    # ── Langkah 2: Huffman decode pixel data ──
    compressed_pixels = data[pos:]
    pixel_data = huffman_decode(compressed_pixels)
    
    # ── Langkah 3: Rekonstruksi image ──
    try:
        img = Image.frombytes(mode, (width, height), pixel_data)
    except Exception as e:
        raise ValueError(f"Failed to reconstruct image: {str(e)}")
    
    # Simpan sebagai PNG (lossless format)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_dir = os.path.dirname(input_path).replace('input', 'output')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(
        output_dir,
        f"{base_name}_decompressed.png"
    )
    img.save(output_path, format='PNG')
    
    # ── Kalkulasi statistik ──
    processing_time = time.time() - start_time
    compressed_size = os.path.getsize(input_path)
    decompressed_size = os.path.getsize(output_path)
    
    return {
        'output_path': output_path,
        'compressed_size': compressed_size,
        'decompressed_size': decompressed_size,
        'processing_time': round(processing_time, 3),
        'width': width,
        'height': height,
        'mode': mode
    }
