"""
lsb.py — Implementasi LSB (Least Significant Bit) Steganography dari Nol

LSB Steganography menyembunyikan pesan di dalam data carrier (image/audio/video)
dengan memodifikasi bit paling tidak signifikan (LSB) dari setiap byte carrier.

Prinsip dasar:
- Setiap byte punya 8 bit: [b7 b6 b5 b4 b3 b2 b1 b0]
- LSB adalah b0 (bit paling kanan)
- Mengubah LSB hanya mengubah nilai byte sebesar ±1
- Untuk image: pixel value 200 jadi 200 atau 201 — perbedaan tidak terlihat mata
- Untuk audio: sample value berubah ±1 — perbedaan tidak terdengar telinga

Format pesan yang di-embed:
┌──────────────────────────────────────────────────────┐
│ Length Prefix (32 bits / 4 bytes)                     │ ← Panjang pesan dalam bytes
│ Message Data (N × 8 bits)                            │ ← Pesan yang disembunyikan
│ Sisa carrier bytes tidak dimodifikasi                │
└──────────────────────────────────────────────────────┘

Setiap bit pesan disimpan di LSB dari 1 byte carrier.
Jadi untuk menyembunyikan 1 karakter (8 bits), butuh 8 bytes carrier.
Total capacity = jumlah carrier bytes / 8 (dalam karakter).
"""


# ─── Konstanta ──────────────────────────────────────────────────────
HEADER_BITS = 32  # 4 bytes untuk length prefix


def calculate_capacity(carrier_data):
    """
    Hitung kapasitas maksimum pesan yang bisa disembunyikan.
    
    Args:
        carrier_data (bytearray): Array byte carrier (pixel values, audio samples, dll)
    
    Returns:
        int: Jumlah maksimum karakter (bytes) yang bisa di-embed
    
    Contoh:
        Carrier 1000 bytes → kapasitas = (1000 - 32) / 8 = 121 karakter
    """
    available_bits = len(carrier_data) - HEADER_BITS
    if available_bits <= 0:
        return 0
    return available_bits // 8


def message_to_bits(message):
    """
    Konversi pesan string menjadi string biner.
    
    Proses:
    1. Encode string ke UTF-8 bytes
    2. Konversi setiap byte ke representasi biner 8-bit
    
    Args:
        message (str): Pesan yang akan disembunyikan
    
    Returns:
        str: String biner (e.g., "01001000011001010110110001101100" untuk "Hell")
    
    Contoh:
        >>> message_to_bits("Hi")
        '0100100001101001'  # H=01001000, i=01101001
    """
    message_bytes = message.encode('utf-8')
    bits = ''.join(f'{byte:08b}' for byte in message_bytes)
    return bits


def bits_to_message(bits):
    """
    Konversi string biner kembali menjadi pesan string.
    
    Args:
        bits (str): String biner (kelipatan 8)
    
    Returns:
        str: Pesan yang sudah di-decode
    """
    # Potong agar panjang kelipatan 8
    bits = bits[:len(bits) - (len(bits) % 8)]
    
    message_bytes = bytearray()
    for i in range(0, len(bits), 8):
        byte = int(bits[i:i+8], 2)
        message_bytes.append(byte)
    
    return message_bytes.decode('utf-8')


def embed(carrier_data, message):
    """
    EMBED: Sisipkan pesan ke dalam carrier data menggunakan LSB.
    
    Algoritma step-by-step:
    1. Konversi panjang pesan (dalam bytes) ke 32-bit binary (length prefix)
    2. Konversi pesan ke binary string
    3. Gabungkan: length_prefix + message_bits
    4. Untuk setiap bit yang akan di-embed:
       a. Ambil byte carrier saat ini
       b. Clear LSB: carrier_byte & 0xFE (set bit terakhir ke 0)
       c. Set LSB ke bit pesan: carrier_byte | message_bit
       d. Simpan byte yang sudah dimodifikasi
    5. Byte carrier sisanya tidak diubah
    
    Args:
        carrier_data (bytearray): Array byte carrier — AKAN DIMODIFIKASI IN-PLACE
        message (str): Pesan yang akan disembunyikan
    
    Returns:
        bytearray: Carrier data yang sudah berisi pesan tersembunyi
        
    Raises:
        ValueError: Jika pesan terlalu panjang untuk carrier
    """
    # Encode pesan ke bytes, lalu hitung panjangnya
    message_bytes = message.encode('utf-8')
    message_length = len(message_bytes)
    
    # Cek kapasitas
    max_capacity = calculate_capacity(carrier_data)
    if message_length > max_capacity:
        raise ValueError(
            f"Message too long ({message_length} bytes). "
            f"Maximum capacity for this file: {max_capacity} bytes. "
            f"Please use a shorter message or a larger carrier file."
        )
    
    # ── Langkah 1: Buat length prefix (32-bit, big-endian) ──
    # Ini disimpan di awal agar saat extract kita tahu berapa panjang pesan
    length_bits = f'{message_length:032b}'
    
    # ── Langkah 2: Konversi pesan ke bits ──
    message_bits = ''.join(f'{byte:08b}' for byte in message_bytes)
    
    # ── Langkah 3: Gabungkan ──
    all_bits = length_bits + message_bits
    
    # ── Langkah 4: Embed setiap bit ke LSB carrier ──
    for i, bit in enumerate(all_bits):
        # Clear LSB (set ke 0) lalu set ke bit pesan
        # Contoh: carrier = 11010101 (213)
        #         & 0xFE  = 11010100 (212) ← clear LSB
        #         | bit 1 = 11010101 (213) ← set LSB ke 1
        #         | bit 0 = 11010100 (212) ← set LSB ke 0
        carrier_data[i] = (carrier_data[i] & 0xFE) | int(bit)
    
    return carrier_data


def extract(carrier_data):
    """
    EXTRACT: Ekstrak pesan tersembunyi dari carrier data.
    
    Algoritma step-by-step:
    1. Baca 32 bit pertama dari LSB carrier → length prefix
    2. Konversi length prefix ke integer → panjang pesan dalam bytes
    3. Baca (panjang × 8) bit berikutnya dari LSB carrier
    4. Konversi bits ke bytes → decode sebagai UTF-8 string
    
    Args:
        carrier_data (bytearray or bytes): Carrier data yang berisi pesan tersembunyi
    
    Returns:
        str: Pesan yang berhasil diekstrak
        
    Raises:
        ValueError: Jika tidak ada pesan valid yang ditemukan
    """
    if len(carrier_data) < HEADER_BITS:
        raise ValueError("Carrier data too small to contain a hidden message")
    
    # ── Langkah 1: Baca length prefix (32 bits dari LSB) ──
    length_bits = ''
    for i in range(HEADER_BITS):
        # Ambil LSB dari setiap byte: byte & 0x01
        # Contoh: byte 11010101 & 00000001 = 1
        length_bits += str(carrier_data[i] & 0x01)
    
    # ── Langkah 2: Konversi ke integer ──
    message_length = int(length_bits, 2)
    
    # Validasi: panjang pesan harus masuk akal
    max_possible = calculate_capacity(carrier_data)
    if message_length <= 0 or message_length > max_possible:
        raise ValueError(
            f"No valid hidden message found. "
            f"Extracted length ({message_length}) is invalid. "
            f"This file might not contain a hidden message."
        )
    
    # ── Langkah 3: Baca message bits ──
    total_message_bits = message_length * 8
    start = HEADER_BITS
    end = start + total_message_bits
    
    if end > len(carrier_data):
        raise ValueError("Carrier data is too small for the indicated message length")
    
    message_bits = ''
    for i in range(start, end):
        message_bits += str(carrier_data[i] & 0x01)
    
    # ── Langkah 4: Konversi bits ke string ──
    try:
        message = bits_to_message(message_bits)
    except UnicodeDecodeError:
        raise ValueError(
            "Failed to decode hidden message. "
            "The file might not contain a valid hidden message, "
            "or the message was embedded using a different method."
        )
    
    return message
