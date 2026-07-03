"""
audio_stego.py — Steganografi Audio menggunakan LSB

Menyembunyikan pesan teks di dalam file audio (.wav) dengan memodifikasi
Least Significant Bit (LSB) dari data PCM (Pulse-Code Modulation).

Alur Embed:
1. Baca file .wav dengan library wave bawaan Python
2. Ekstrak raw PCM frames ke dalam bytearray
3. Cek kapasitas (apakah frame cukup untuk pesan)
4. Embed pesan ke LSB frame
5. Simpan kembali frame yang sudah dimodifikasi ke file .wav baru

Alur Extract:
1. Baca stego .wav
2. Ekstrak raw PCM frames
3. Ekstrak pesan menggunakan LSB
4. Return pesan
"""

import os
import time
import wave

from modules.steganography.lsb import embed, extract, calculate_capacity


def embed_message(audio_path, message):
    """
    Sisipkan pesan tersembunyi ke dalam audio menggunakan LSB.
    """
    start_time = time.time()
    
    # ── Langkah 1: Baca audio ──
    try:
        with wave.open(audio_path, 'rb') as wav_file:
            channels = wav_file.getnchannels()
            sampwidth = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            nframes = wav_file.getnframes()
            
            pcm_data = bytearray(wav_file.readframes(nframes))
    except Exception as e:
        raise ValueError(f"Cannot read WAV file: {str(e)}")
    
    # ── Langkah 2: Cek kapasitas ──
    capacity = calculate_capacity(pcm_data)
    message_bytes_len = len(message.encode('utf-8'))
    
    if message_bytes_len > capacity:
        raise ValueError(
            f"Message too long! Your message is {message_bytes_len} bytes, "
            f"but this audio can only hide {capacity} bytes. "
            f"Use a longer audio file or a shorter message."
        )
    
    # ── Langkah 3: Embed pesan ──
    stego_data = embed(pcm_data, message)
    
    # ── Langkah 4: Simpan sebagai .wav baru ──
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    output_path = os.path.join(
        os.path.dirname(audio_path).replace('input', 'output'),
        f"{base_name}_stego.wav"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        with wave.open(output_path, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sampwidth)
            wav_file.setframerate(framerate)
            wav_file.writeframes(bytes(stego_data))
    except Exception as e:
        raise ValueError(f"Failed to save stego audio: {str(e)}")
    
    # ── Kalkulasi statistik ──
    processing_time = time.time() - start_time
    original_size = os.path.getsize(audio_path)
    stego_size = os.path.getsize(output_path)
    
    return {
        'output_path': output_path,
        'original_size': original_size,
        'stego_size': stego_size,
        'message_length': message_bytes_len,
        'capacity': capacity,
        'usage_percent': round((message_bytes_len / capacity) * 100, 2) if capacity > 0 else 0,
        'processing_time': round(processing_time, 3)
    }


def extract_message(audio_path):
    """
    Ekstrak pesan tersembunyi dari stego audio.
    """
    start_time = time.time()
    
    # ── Langkah 1: Baca audio ──
    try:
        with wave.open(audio_path, 'rb') as wav_file:
            nframes = wav_file.getnframes()
            pcm_data = bytearray(wav_file.readframes(nframes))
    except Exception as e:
        raise ValueError(f"Cannot read WAV file: {str(e)}")
    
    # ── Langkah 2: Extract pesan ──
    message = extract(pcm_data)
    
    processing_time = time.time() - start_time
    
    return {
        'message': message,
        'message_length': len(message),
        'processing_time': round(processing_time, 3)
    }
