"""
video_codec.py — Kompresi dan Dekompresi Video menggunakan Huffman

Karena meng-extract raw frame dari video 1080p dengan Python murni 
akan memakan RAM hingga puluhan GB, metode yang digunakan untuk Video
adalah Binary File Archiving menggunakan Huffman Coding.

Alur Kompresi:
1. Baca file video secara binary
2. Encode seluruh bytes menggunakan algoritma Huffman
3. Simpan ekstensi file asli di header
4. Simpan hasil sebagai .mvault
"""

import os
import struct
import time

from modules.compression.huffman import encode as huffman_encode, decode as huffman_decode


# Format header file .mvault untuk video:
# ┌──────────────────────────────────────────────┐
# │ Magic: "VMVT" (4 bytes)                      │ ← Video Media Vault
# │ Ext Length (1 byte, unsigned char)           │ ← Panjang string ekstensi
# │ Extension String (n bytes)                   │ ← misal: ".mp4"
# │ Huffman-encoded video binary data            │
# └──────────────────────────────────────────────┘

VIDEO_MAGIC = b'VMVT'


def compress_video(input_path):
    start_time = time.time()
    
    # ── Langkah 1: Baca file ──
    try:
        with open(input_path, 'rb') as f:
            video_data = f.read()
    except Exception as e:
        raise ValueError(f"Cannot read video file: {str(e)}")
    
    # ── Langkah 2: Ekstrak ekstensi ──
    _, ext = os.path.splitext(input_path)
    ext_bytes = ext.encode('utf-8')
    ext_len = len(ext_bytes)
    
    if ext_len > 255:
        raise ValueError("File extension is too long.")
    
    # ── Langkah 3: Bangun header ──
    header = bytearray()
    header.extend(VIDEO_MAGIC)                           # Magic number
    header.append(ext_len)                               # Ext Length (1 byte)
    header.extend(ext_bytes)                             # Extension String
    
    # ── Langkah 4: Huffman encode data ──
    compressed_data = huffman_encode(video_data)
    
    # ── Langkah 5: Gabungkan header + compressed data ──
    output_data = bytes(header) + compressed_data
    
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
    original_size = len(video_data)
    compressed_size = len(output_data)
    compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
    
    return {
        'output_path': output_path,
        'original_size': original_size,
        'original_raw_size': original_size, # Untuk video binary, raw size = file size
        'compressed_size': compressed_size,
        'compression_ratio': round(compression_ratio, 2),
        'processing_time': round(processing_time, 3)
    }


def decompress_video(input_path):
    start_time = time.time()
    
    with open(input_path, 'rb') as f:
        data = f.read()
    
    pos = 0
    
    # ── Langkah 1: Baca header ──
    magic = data[pos:pos+4]
    pos += 4
    if magic != VIDEO_MAGIC:
        raise ValueError(f"Invalid video vault file. Expected 'VMVT' header, got '{magic}'")
    
    ext_len = data[pos]
    pos += 1
    
    ext_bytes = data[pos:pos+ext_len]
    ext = ext_bytes.decode('utf-8')
    pos += ext_len
    
    # ── Langkah 2: Huffman decode ──
    compressed_data = data[pos:]
    video_data = huffman_decode(compressed_data)
    
    # ── Langkah 3: Rekonstruksi file video ──
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    # Hapus suffix _compressed jika ada
    if base_name.endswith('_compressed'):
        base_name = base_name[:-11]
        
    output_dir = os.path.dirname(input_path).replace('input', 'output')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(
        output_dir,
        f"{base_name}_decompressed{ext}"
    )
    
    with open(output_path, 'wb') as f:
        f.write(video_data)
    
    # ── Kalkulasi statistik ──
    processing_time = time.time() - start_time
    compressed_size = os.path.getsize(input_path)
    decompressed_size = len(video_data)
    
    return {
        'output_path': output_path,
        'compressed_size': compressed_size,
        'decompressed_size': decompressed_size,
        'processing_time': round(processing_time, 3)
    }
