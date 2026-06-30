"""
rle.py — Implementasi Run-Length Encoding (RLE) dari Nol

RLE adalah algoritma kompresi lossless yang sangat sederhana:
- Scan data dari kiri ke kanan
- Hitung jumlah byte berturut-turut yang sama (run)
- Simpan sebagai pasangan (count, byte_value)

Contoh:
  Input:  AAABBCCCCDD
  Encode: (3,A)(2,B)(4,C)(2,D)

Efektif untuk data dengan banyak byte berulang (misal: area warna solid di image).
Tidak efektif untuk data random (bisa malah lebih besar dari asli).

Catatan: RLE digunakan sebagai algoritma pendamping Huffman di project ini.
Untuk data tertentu, RLE+Huffman bisa lebih efektif daripada Huffman saja.

Format output:
┌──────────────────────────────────────────┐
│ Magic Number: "RVLT" (4 bytes)           │
│ Panjang Data Asli (4 bytes, big-endian)  │
│ RLE Pairs:                               │
│   [count (1B)] [byte_value (1B)] × N     │
│   count: 1-255 (run > 255 = split)       │
└──────────────────────────────────────────┘
"""

import struct


def encode(data):
    """
    ENCODE: Kompresi data menggunakan Run-Length Encoding.
    
    Proses:
    1. Iterasi setiap byte dalam data
    2. Hitung berapa kali byte yang sama muncul berturut-turut (run length)
    3. Jika run length > 255, pecah jadi beberapa pasangan (max count = 255)
    4. Tulis pasangan (count, byte) ke output
    
    Args:
        data (bytes): Data mentah yang akan dikompresi
    
    Returns:
        bytes: Data terkompresi dalam format RLE
        
    Raises:
        ValueError: Jika data kosong
    
    Contoh:
        >>> encode(b'AAABBBCC')
        b'RVLT\\x00\\x00\\x00\\x08\\x03A\\x03B\\x02C'
    """
    if not data:
        raise ValueError("Cannot encode empty data")
    
    result = bytearray()
    
    # Header
    result.extend(b'RVLT')                          # Magic number
    result.extend(struct.pack('>I', len(data)))      # Panjang data asli
    
    # RLE encoding
    i = 0
    while i < len(data):
        current_byte = data[i]
        count = 1
        
        # Hitung berapa kali byte yang sama muncul berturut-turut
        while i + count < len(data) and data[i + count] == current_byte and count < 255:
            count += 1
        
        # Tulis pasangan (count, byte)
        result.append(count)
        result.append(current_byte)
        
        i += count
    
    return bytes(result)


def decode(compressed_data):
    """
    DECODE: Dekompresi data dari format RLE kembali ke data asli.
    
    Proses:
    1. Baca header: magic number, panjang data asli
    2. Baca setiap pasangan (count, byte)
    3. Expand: ulangi byte sebanyak count kali
    4. Verifikasi panjang hasil = panjang asli
    
    Args:
        compressed_data (bytes): Data terkompresi dalam format RLE
    
    Returns:
        bytes: Data asli yang sudah di-dekompresi
        
    Raises:
        ValueError: Jika format file tidak valid
    """
    if len(compressed_data) < 8:
        raise ValueError("Compressed data too small — file might be corrupted")
    
    pos = 0
    
    # Baca header
    magic = compressed_data[pos:pos+4]
    pos += 4
    if magic != b'RVLT':
        raise ValueError(f"Invalid RLE format. Expected 'RVLT' header, got '{magic}'")
    
    original_length = struct.unpack('>I', compressed_data[pos:pos+4])[0]
    pos += 4
    
    # Decode RLE pairs
    decoded = bytearray()
    while pos + 1 < len(compressed_data):
        count = compressed_data[pos]
        byte_value = compressed_data[pos + 1]
        pos += 2
        
        # Expand: ulangi byte sebanyak count kali
        decoded.extend(bytes([byte_value]) * count)
    
    # Verifikasi panjang
    if len(decoded) != original_length:
        raise ValueError(
            f"Decompressed size mismatch: got {len(decoded)}, expected {original_length}. "
            "File might be corrupted."
        )
    
    return bytes(decoded)
