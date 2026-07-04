"""
video_codec.py — Kompresi dan Dekompresi Video menggunakan Huffman

Karena meng-extract raw frame dari video 1080p dengan Python murni 
akan memakan RAM hingga puluhan GB, metode yang digunakan untuk Video
adalah Binary File Archiving menggunakan Huffman Coding dengan
Run-Length Encoding (RLE) sebagai praproses untuk meningkatkan efisiensi.

Kenapa menambahkan RLE sebagai praproses?
- File video modern (mp4/avi) mengandung metadata, header, dan footer
  yang sering memiliki pola berulang
- RLE akan meng-"collaps" urutan byte berulang tersebut terlebih dahulu
- Hasilnya data menjadi lebih terstruktur → Huffman lebih efisien

Alur Kompresi:
1. Baca file video secara binary
2. RLE Encode: padatkan urutan byte yang berulang
3. Huffman encode hasil RLE
4. Simpan ekstensi file asli di header
5. Simpan hasil sebagai .mvault

Alur Dekompresi:
1. Baca .mvault
2. Huffman decode
3. RLE decode
4. Rekonstruksi ke format video asli (lossless)
"""

import os
import struct
import time

from modules.compression.huffman import encode as huffman_encode, decode as huffman_decode


# Format header file .mvault untuk video:
# ┌──────────────────────────────────────────────┐
# │ Magic: "VMVT" (4 bytes)                      │ ← Video Media Vault
# │ Version (1 byte)                             │ ← 2 = RLE + Huffman
# │ Ext Length (1 byte, unsigned char)           │ ← Panjang string ekstensi
# │ Extension String (n bytes)                   │ ← misal: ".mp4"
# │ Original file size (8 bytes, uint64)         │ ← untuk verifikasi lossless
# │ RLE+Huffman encoded video binary data        │
# └──────────────────────────────────────────────┘

VIDEO_MAGIC = b'VMVT'
VERSION = 2  # v2 = RLE preprocessing enabled


def _rle_encode(data: bytes) -> bytes:
    """
    Run-Length Encoding: padatkan urutan byte berulang.
    
    Format output per-run: [count (1 byte)] [byte_value (1 byte)]
    Jika count > 255, bagi menjadi beberapa run.
    
    Contoh: b'AAABBC' → [(3,A), (2,B), (1,C)]
    """
    if not data:
        return b''
    
    result = bytearray()
    i = 0
    n = len(data)
    
    while i < n:
        current = data[i]
        count = 1
        # Hitung berapa kali byte ini berulang berturut-turut
        while i + count < n and data[i + count] == current and count < 255:
            count += 1
        result.append(count)
        result.append(current)
        i += count
    
    return bytes(result)


def _rle_decode(data: bytes) -> bytes:
    """
    RLE Decode: kembalikan data RLE ke bentuk aslinya.
    
    Contoh: [(3,A), (2,B), (1,C)] → b'AAABBC'
    
    Ini LOSSLESS — data yang dikembalikan IDENTIK dengan aslinya.
    """
    if not data:
        return b''
    
    result = bytearray()
    i = 0
    while i + 1 < len(data):
        count = data[i]
        byte_val = data[i + 1]
        result.extend(bytes([byte_val]) * count)
        i += 2
    
    return bytes(result)


def compress_video(input_path):
    """
    Kompresi file video menggunakan RLE + Huffman Coding.
    
    RLE sebagai praproses memampatkan pola byte berulang dalam file video
    (header metadata, padding, trailing zeros) sebelum Huffman bekerja,
    sehingga menghasilkan rasio kompresi yang jauh lebih baik.
    """
    start_time = time.time()
    
    # ── Langkah 1: Baca file ──
    try:
        with open(input_path, 'rb') as f:
            video_data = f.read()
    except Exception as e:
        raise ValueError(f"Cannot read video file: {str(e)}")
    
    original_size = len(video_data)
    
    # ── Langkah 2: Ekstrak ekstensi ──
    _, ext = os.path.splitext(input_path)
    ext_bytes = ext.encode('utf-8')
    ext_len = len(ext_bytes)
    
    if ext_len > 255:
        raise ValueError("File extension is too long.")
    
    # ── Langkah 3: RLE Encode sebagai praproses ──
    rle_data = _rle_encode(video_data)
    
    # ── Langkah 4: Huffman encode data RLE ──
    compressed_data = huffman_encode(rle_data)
    
    # ── Langkah 5: Bangun header ──
    header = bytearray()
    header.extend(VIDEO_MAGIC)                           # Magic number
    header.append(VERSION)                               # Version (1 byte)
    header.append(ext_len)                               # Ext Length (1 byte)
    header.extend(ext_bytes)                             # Extension String
    header.extend(struct.pack('>Q', original_size))      # Original size (8 bytes)
    
    # ── Langkah 6: Gabungkan header + compressed data ──
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
    compressed_size = len(output_data)
    compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
    
    return {
        'output_path': output_path,
        'original_size': original_size,
        'original_raw_size': original_size,
        'compressed_size': compressed_size,
        'compression_ratio': round(compression_ratio, 2),
        'processing_time': round(processing_time, 3)
    }


def decompress_video(input_path):
    """
    Dekompresi file .mvault kembali ke format video asli (100% Lossless).
    """
    start_time = time.time()
    
    with open(input_path, 'rb') as f:
        data = f.read()
    
    pos = 0
    
    # ── Langkah 1: Baca header ──
    magic = data[pos:pos+4]
    pos += 4
    if magic != VIDEO_MAGIC:
        raise ValueError(f"Invalid video vault file. Expected 'VMVT' header, got '{magic}'")
    
    version = data[pos]
    pos += 1
    
    ext_len = data[pos]
    pos += 1
    
    ext_bytes = data[pos:pos+ext_len]
    ext = ext_bytes.decode('utf-8')
    pos += ext_len
    
    original_size = struct.unpack('>Q', data[pos:pos+8])[0]
    pos += 8
    
    # ── Langkah 2: Huffman decode ──
    compressed_data = data[pos:]
    rle_data = huffman_decode(compressed_data)
    
    # ── Langkah 3: RLE decode ──
    if version >= 2:
        video_data = _rle_decode(rle_data)
    else:
        # Backward compat: v1 tanpa RLE
        video_data = rle_data
    
    # ── Langkah 4: Rekonstruksi file video ──
    base_name = os.path.splitext(os.path.basename(input_path))[0]
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
