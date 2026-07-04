"""
audio_codec.py — Kompresi dan Dekompresi Audio (.wav)

Menggunakan Huffman Coding dengan Delta Encoding (praproses) untuk
mengkompresi raw PCM data dari audio.

Kenapa Delta Encoding?
- Raw PCM audio memiliki entropy tinggi → Huffman tidak bisa kompres banyak
- Delta Encoding: ganti setiap sample dengan SELISIH dari sample sebelumnya
- Data selisih (delta) cenderung mendekati nol → sangat berulang → Huffman efisien!

Alur kompresi:
1. Baca file .wav → ambil header metadata (channels, width, rate)
2. Ambil raw PCM frames → konversi ke array sample integers
3. Delta Encode: hitung selisih antar sample berurutan
4. Huffman encode delta data
5. Output: file .mvault

Alur dekompresi:
1. Baca file .mvault → extract header metadata
2. Huffman decode → delta data
3. Delta Decode: kembalikan ke sample asli (cumulative sum)
4. Rekonstruksi file .wav
5. Output: file audio (.wav — lossless)
"""

import os
import struct
import time
import wave

from modules.compression.huffman import encode as huffman_encode, decode as huffman_decode


# Format header file .mvault untuk audio:
# ┌──────────────────────────────────────────────┐
# │ Magic: "AMVT" (4 bytes)                      │ ← Audio Media Vault
# │ Version (1 byte)                             │ ← 2 = with delta encoding
# │ Channels (2 bytes, unsigned short)           │
# │ Sample Width (2 bytes, unsigned short)       │
# │ Framerate (4 bytes, unsigned int)            │
# │ Num Frames (4 bytes, unsigned int)           │
# │ Huffman-encoded delta data                   │
# └──────────────────────────────────────────────┘

AUDIO_MAGIC = b'AMVT'
VERSION = 2  # v2 = delta encoding enabled


def _pcm_to_samples(pcm_data, sampwidth):
    """
    Konversi raw PCM bytes menjadi list of integers (audio samples).
    Mendukung 8-bit (unsigned), 16-bit (signed), dan 32-bit (signed).
    """
    import array
    if sampwidth == 1:
        # 8-bit unsigned
        samples = list(pcm_data)
    elif sampwidth == 2:
        # 16-bit signed little-endian
        arr = array.array('h')
        arr.frombytes(pcm_data)
        samples = list(arr)
    elif sampwidth == 4:
        # 32-bit signed little-endian
        arr = array.array('i')
        arr.frombytes(pcm_data)
        samples = list(arr)
    else:
        raise ValueError(f"Unsupported sample width: {sampwidth}")
    return samples


def _samples_to_pcm(samples, sampwidth):
    """
    Konversi list of integers kembali menjadi raw PCM bytes.
    """
    import array
    if sampwidth == 1:
        return bytes(samples)
    elif sampwidth == 2:
        arr = array.array('h', samples)
        return arr.tobytes()
    elif sampwidth == 4:
        arr = array.array('i', samples)
        return arr.tobytes()
    else:
        raise ValueError(f"Unsupported sample width: {sampwidth}")


def _delta_encode(samples):
    """
    Delta Encoding: ubah setiap sample menjadi selisih (delta) dari sample sebelumnya.
    
    Contoh: [100, 102, 101, 105] → [100, 2, -1, 4]
    
    Data delta mendekati nol → sangat berulang → Huffman sangat efisien!
    """
    if not samples:
        return []
    deltas = [samples[0]]
    for i in range(1, len(samples)):
        deltas.append(samples[i] - samples[i - 1])
    return deltas


def _delta_decode(deltas):
    """
    Delta Decoding: kembalikan delta kembali ke samples asli (cumulative sum).
    
    Contoh: [100, 2, -1, 4] → [100, 102, 101, 105]
    
    Ini LOSSLESS — samples yang dikembalikan IDENTIK dengan aslinya.
    """
    if not deltas:
        return []
    samples = [deltas[0]]
    for i in range(1, len(deltas)):
        samples.append(samples[-1] + deltas[i])
    return samples


def _pack_signed_shorts(deltas, sampwidth):
    """
    Packing delta values menjadi bytes untuk di-Huffman encode.
    Menggunakan 2 bytes per delta (signed short, big-endian) agar kompatibel
    dengan berbagai sampwidth.
    """
    result = bytearray()
    for d in deltas:
        # Clamp ke range int16 untuk keamanan packing
        clamped = max(-32768, min(32767, d))
        result.extend(struct.pack('>h', clamped))
    return bytes(result)


def _unpack_signed_shorts(data):
    """
    Unpack delta bytes kembali menjadi list of signed integers.
    """
    n = len(data) // 2
    return [struct.unpack('>h', data[i*2:(i*2)+2])[0] for i in range(n)]


def compress_audio(input_path):
    """
    Kompresi file .wav menggunakan Huffman Coding + Delta Encoding.
    Delta Encoding sebagai praproses memastikan Huffman bisa bekerja
    jauh lebih efisien pada data audio yang sebelumnya high-entropy.
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
    
    # ── Langkah 2: PCM → Samples → Delta Encode ──
    samples = _pcm_to_samples(pcm_data, sampwidth)
    deltas = _delta_encode(samples)
    delta_bytes = _pack_signed_shorts(deltas, sampwidth)
    
    # ── Langkah 3: Bangun header ──
    header = bytearray()
    header.extend(AUDIO_MAGIC)                           # Magic number
    header.append(VERSION)                               # Version (1 byte)
    header.extend(struct.pack('>H', channels))           # Channels (2 bytes)
    header.extend(struct.pack('>H', sampwidth))          # Sample Width (2 bytes)
    header.extend(struct.pack('>I', framerate))          # Framerate (4 bytes)
    header.extend(struct.pack('>I', nframes))            # Num frames (4 bytes)
    
    # ── Langkah 4: Huffman encode delta data ──
    compressed_deltas = huffman_encode(delta_bytes)
    
    # ── Langkah 5: Gabungkan header + compressed data ──
    output_data = bytes(header) + compressed_deltas
    
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
    # Bandingkan vs raw PCM (bukan file .wav dengan header)
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
    Dekompresi file .mvault kembali menjadi .wav (100% Lossless).
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
    
    version = data[pos]
    pos += 1
    
    channels = struct.unpack('>H', data[pos:pos+2])[0]
    pos += 2
    sampwidth = struct.unpack('>H', data[pos:pos+2])[0]
    pos += 2
    framerate = struct.unpack('>I', data[pos:pos+4])[0]
    pos += 4
    nframes = struct.unpack('>I', data[pos:pos+4])[0]
    pos += 4
    
    # ── Langkah 2: Huffman decode → delta bytes ──
    compressed_data = data[pos:]
    delta_bytes = huffman_decode(compressed_data)
    
    # ── Langkah 3: Unpack delta → Delta Decode → PCM ──
    if version >= 2:
        deltas = _unpack_signed_shorts(delta_bytes)
        samples = _delta_decode(deltas)
        # Potong ke jumlah sample yang sebenarnya (channels × nframes)
        expected = nframes * channels
        samples = samples[:expected]
        pcm_data = _samples_to_pcm(samples, sampwidth)
    else:
        # Backward compat: v1 tanpa delta encoding
        pcm_data = delta_bytes
    
    # ── Langkah 4: Rekonstruksi file .wav ──
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
