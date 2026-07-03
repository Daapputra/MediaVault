"""
video_stego.py — Steganografi Video menggunakan EOF (End-Of-File) Appending

Teknik: Menyisipkan pesan rahasia di akhir struktur biner file video.
Ini adalah metode steganografi struktural yang:
- Tidak merusak data video sama sekali
- Tidak mengubah kualitas visual/audio video
- Sangat cepat karena tidak perlu decode/encode frame
- File tetap bisa diputar normal di media player manapun

Alur Embed:
1. Baca file video secara binary
2. Tambahkan marker khusus + pesan terenkode di akhir file
3. Simpan sebagai file video baru (ekstensi sama)

Alur Extract:
1. Baca file video secara binary
2. Cari marker di akhir file
3. Ekstrak dan decode pesan

Format EOF:
┌──────────────────────────────────────────────┐
│ [Original Video Data]                        │
│ [MARKER: "MVSTEGO" (7 bytes)]               │
│ [Message Length (4 bytes, big-endian uint)]   │
│ [XOR-encoded Message (N bytes)]              │
│ [FOOTER: "MVEND" (5 bytes)]                  │
└──────────────────────────────────────────────┘
"""

import os
import struct
import time

STEGO_MARKER = b'MVSTEGO'
STEGO_FOOTER = b'MVEND'
XOR_KEY = 0xA5  # Simple XOR key for basic obfuscation


def _xor_encode(data):
    """XOR encode/decode data untuk obfuscation sederhana."""
    return bytes([b ^ XOR_KEY for b in data])


def embed_message(video_path, message):
    """
    Sisipkan pesan tersembunyi ke akhir file video menggunakan EOF steganography.
    """
    start_time = time.time()
    
    # ── Langkah 1: Baca file video ──
    try:
        with open(video_path, 'rb') as f:
            video_data = f.read()
    except Exception as e:
        raise ValueError(f"Cannot read video file: {str(e)}")
    
    # ── Langkah 2: Cek apakah sudah ada pesan tersembunyi ──
    if video_data[-len(STEGO_FOOTER):] == STEGO_FOOTER:
        raise ValueError(
            "This video already contains a hidden message. "
            "Please use a clean video file."
        )
    
    # ── Langkah 3: Encode pesan ──
    message_bytes = message.encode('utf-8')
    encoded_message = _xor_encode(message_bytes)
    message_length = len(encoded_message)
    
    # ── Langkah 4: Bangun payload ──
    payload = bytearray()
    payload.extend(STEGO_MARKER)                                    # 7 bytes marker
    payload.extend(struct.pack('>I', message_length))               # 4 bytes length
    payload.extend(encoded_message)                                 # N bytes message
    payload.extend(STEGO_FOOTER)                                    # 5 bytes footer
    
    # ── Langkah 5: Gabungkan video + payload ──
    stego_data = video_data + bytes(payload)
    
    # ── Langkah 6: Simpan file ──
    _, ext = os.path.splitext(video_path)
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_path = os.path.join(
        os.path.dirname(video_path).replace('input', 'output'),
        f"{base_name}_stego{ext}"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'wb') as f:
        f.write(stego_data)
    
    # ── Kalkulasi statistik ──
    processing_time = time.time() - start_time
    original_size = len(video_data)
    stego_size = len(stego_data)
    
    return {
        'output_path': output_path,
        'original_size': original_size,
        'stego_size': stego_size,
        'message_length': len(message_bytes),
        'capacity': original_size,  # Theoretically can hide very large messages
        'usage_percent': round((len(message_bytes) / max(original_size, 1)) * 100, 4),
        'processing_time': round(processing_time, 3)
    }


def extract_message(video_path):
    """
    Ekstrak pesan tersembunyi dari file video yang sudah di-embed.
    """
    start_time = time.time()
    
    # ── Langkah 1: Baca file video ──
    try:
        with open(video_path, 'rb') as f:
            video_data = f.read()
    except Exception as e:
        raise ValueError(f"Cannot read video file: {str(e)}")
    
    # ── Langkah 2: Cek footer ──
    if video_data[-len(STEGO_FOOTER):] != STEGO_FOOTER:
        raise ValueError(
            "No hidden message found in this video. "
            "Make sure you uploaded a video that was embedded using this system."
        )
    
    # ── Langkah 3: Parse payload dari belakang ──
    # Layout: [video][MARKER(7)][LENGTH(4)][MESSAGE(N)][FOOTER(5)]
    footer_pos = len(video_data) - len(STEGO_FOOTER)
    
    # Cari marker dari belakang
    marker_search_start = max(0, footer_pos - 10 * 1024 * 1024)  # Search last 10MB
    marker_pos = video_data.rfind(STEGO_MARKER, marker_search_start)
    
    if marker_pos == -1:
        raise ValueError("Corrupted stego data: marker not found.")
    
    # Baca message length
    length_pos = marker_pos + len(STEGO_MARKER)
    message_length = struct.unpack('>I', video_data[length_pos:length_pos+4])[0]
    
    # Baca encoded message
    message_start = length_pos + 4
    encoded_message = video_data[message_start:message_start + message_length]
    
    if len(encoded_message) != message_length:
        raise ValueError("Corrupted stego data: message length mismatch.")
    
    # ── Langkah 4: Decode pesan ──
    message_bytes = _xor_encode(encoded_message)
    message = message_bytes.decode('utf-8')
    
    processing_time = time.time() - start_time
    
    return {
        'message': message,
        'message_length': len(message),
        'processing_time': round(processing_time, 3)
    }
