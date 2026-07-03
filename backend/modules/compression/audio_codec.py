"""
audio_codec.py — Kompresi dan Dekompresi Audio (.wav)

Menggunakan Huffman Coding untuk mengkompresi raw PCM data dari audio.
Hanya mendukung format file .wav (lossless audio).

Alur kompresi:
1. Baca file .wav → ambil header metadata (channels, width, rate)
2. Ambil raw PCM frames (bytes)
3. Huffman encode PCM data
4. Output: file .mvault

Alur dekompresi:
1. Baca file .mvault → extract header metadata
2. Huffman decode PCM data
3. Rekonstruksi file .wav
4. Output: file audio (.wav — lossless)
"""

import os
import struct
import time
import wave

from modules.compression.huffman import encode as huffman_encode, decode as huffman_decode


# Format header file .mvault untuk audio:
# ┌──────────────────────────────────────────────┐
# │ Magic: "AMVT" (4 bytes)                      │ ← Audio Media Vault
# │ Channels (2 bytes, unsigned short)           │
# │ Sample Width (2 bytes, unsigned short)       │
# │ Framerate (4 bytes, unsigned int)            │
# │ Huffman-encoded PCM frames data              │
# └──────────────────────────────────────────────┘

AUDIO_MAGIC = b'AMVT'


def compress_audio(input_path):
    """
    Kompresi file .wav menggunakan Huffman Coding.
    """
    start_time = time.time()
    
    # ── Langkah 1: Baca audio dan ambil PCM data ──
    try:
        with wave.open(input_path, 'rb') as wav_file:
            channels = wav_file.getnchannels()
            sampwidth = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            nframes = wav_file.getnframes()
            
            pcm_data = wav_file.readframes(nframes)
    except Exception as e:
        raise ValueError(f"Cannot read WAV file. Ensure it is a valid .wav format: {str(e)}")
    
    # ── Langkah 2: Bangun header ──
    header = bytearray()
    header.extend(AUDIO_MAGIC)                           # Magic number
    header.extend(struct.pack('>H', channels))           # Channels (2 bytes)
    header.extend(struct.pack('>H', sampwidth))          # Sample Width (2 bytes)
    header.extend(struct.pack('>I', framerate))          # Framerate (4 bytes)
    
    # ── Langkah 3: Huffman encode PCM data ──
    compressed_frames = huffman_encode(pcm_data)
    
    # ── Langkah 4: Gabungkan header + compressed data ──
    output_data = bytes(header) + compressed_frames
    
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
    compression_ratio = (1 - compressed_size / len(pcm_data)) * 100 if len(pcm_data) > 0 else 0
    
    return {
        'output_path': output_path,
        'original_size': original_size,
        'original_raw_size': len(pcm_data),
        'compressed_size': compressed_size,
        'compression_ratio': round(compression_ratio, 2),
        'processing_time': round(processing_time, 3)
    }


def decompress_audio(input_path):
    """
    Dekompresi file .mvault kembali menjadi .wav
    """
    start_time = time.time()
    
    with open(input_path, 'rb') as f:
        data = f.read()
    
    pos = 0
    
    # ── Langkah 1: Baca header ──
    magic = data[pos:pos+4]
    pos += 4
    if magic != AUDIO_MAGIC:
        raise ValueError(f"Invalid audio vault file. Expected 'AMVT' header, got '{magic}'")
    
    channels = struct.unpack('>H', data[pos:pos+2])[0]
    pos += 2
    sampwidth = struct.unpack('>H', data[pos:pos+2])[0]
    pos += 2
    framerate = struct.unpack('>I', data[pos:pos+4])[0]
    pos += 4
    
    # ── Langkah 2: Huffman decode PCM data ──
    compressed_frames = data[pos:]
    pcm_data = huffman_decode(compressed_frames)
    
    # ── Langkah 3: Rekonstruksi file .wav ──
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_dir = os.path.dirname(input_path).replace('input', 'output')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(
        output_dir,
        f"{base_name}_decompressed.wav"
    )
    
    try:
        with wave.open(output_path, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sampwidth)
            wav_file.setframerate(framerate)
            wav_file.writeframes(pcm_data)
    except Exception as e:
        raise ValueError(f"Failed to reconstruct audio: {str(e)}")
    
    # ── Kalkulasi statistik ──
    processing_time = time.time() - start_time
    compressed_size = os.path.getsize(input_path)
    decompressed_size = os.path.getsize(output_path)
    
    return {
        'output_path': output_path,
        'compressed_size': compressed_size,
        'decompressed_size': decompressed_size,
        'processing_time': round(processing_time, 3)
    }
