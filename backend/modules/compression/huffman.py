"""
huffman.py — Implementasi Huffman Coding dari Nol

Huffman Coding adalah algoritma kompresi lossless yang bekerja dengan cara:
1. Menghitung frekuensi kemunculan setiap byte dalam data
2. Membangun binary tree (Huffman Tree) berdasarkan frekuensi
3. Byte yang sering muncul mendapat kode biner pendek
4. Byte yang jarang muncul mendapat kode biner panjang
5. Hasilnya: data terkompresi yang ukurannya lebih kecil

Algoritma ini LOSSLESS — data yang di-decode akan persis sama dengan data asli.

Format output file (.mvault):
┌──────────────────────────────────────────┐
│ Magic Number: "HVLT" (4 bytes)           │ ← Identifikasi format
│ Panjang Data Asli (4 bytes, big-endian)  │ ← Untuk alokasi saat decode
│ Jumlah Simbol Unik (2 bytes)            │ ← Untuk rebuild tree
│ Frequency Table:                         │
│   [byte (1B)] [freq (4B)] × N           │ ← Pasangan simbol-frekuensi
│ Padding Bits Count (1 byte)             │ ← Jumlah bit padding di akhir
│ Encoded Bitstream                        │ ← Data terkompresi
└──────────────────────────────────────────┘
"""

import heapq
import struct
from collections import Counter


class HuffmanNode:
    """
    Node dalam Huffman Tree.
    
    Setiap node menyimpan:
    - byte_value: nilai byte (0-255) untuk leaf node, None untuk internal node
    - frequency: frekuensi kemunculan (digunakan untuk priority queue)
    - left, right: child nodes
    
    __lt__ diperlukan agar heapq bisa membandingkan node berdasarkan frekuensi.
    """
    
    def __init__(self, byte_value=None, frequency=0, left=None, right=None):
        self.byte_value = byte_value  # None untuk internal node
        self.frequency = frequency
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        """Perbandingan untuk priority queue — node dengan frekuensi lebih kecil punya prioritas lebih tinggi."""
        return self.frequency < other.frequency
    
    def is_leaf(self):
        """Cek apakah node ini adalah leaf (punya byte value, tidak punya child)."""
        return self.left is None and self.right is None


def count_frequencies(data):
    """
    Langkah 1: Hitung frekuensi setiap byte dalam data.
    
    Args:
        data (bytes): Data mentah yang akan dikompresi
    
    Returns:
        dict: Mapping {byte_value: frequency}
              Contoh: {72: 5, 101: 3, 108: 7} artinya 'H' muncul 5x, 'e' 3x, 'l' 7x
    """
    return dict(Counter(data))


def build_huffman_tree(frequency_table):
    """
    Langkah 2: Bangun Huffman Tree menggunakan priority queue (min-heap).
    
    Algoritma:
    1. Buat leaf node untuk setiap byte unik, masukkan ke min-heap
    2. Selama heap punya lebih dari 1 node:
       a. Ambil 2 node dengan frekuensi terkecil
       b. Gabung jadi 1 internal node (frekuensi = sum keduanya)
       c. Masukkan internal node kembali ke heap
    3. Node terakhir di heap adalah root dari Huffman Tree
    
    Args:
        frequency_table (dict): Mapping {byte_value: frequency}
    
    Returns:
        HuffmanNode: Root node dari Huffman Tree
    """
    if not frequency_table:
        return None
    
    # Buat min-heap dari leaf nodes
    # Format heap: (frequency, tie_breaker, node)
    # tie_breaker mencegah error saat frequency sama
    heap = []
    for byte_val, freq in frequency_table.items():
        node = HuffmanNode(byte_value=byte_val, frequency=freq)
        heapq.heappush(heap, (freq, byte_val, node))
    
    # Edge case: hanya ada 1 simbol unik
    # Tambahkan dummy node agar tree tetap valid (punya setidaknya 2 leaf)
    if len(heap) == 1:
        freq, byte_val, node = heap[0]
        # Buat dummy node dengan byte value yang berbeda
        dummy_val = (byte_val + 1) % 256
        dummy = HuffmanNode(byte_value=dummy_val, frequency=0)
        heapq.heappush(heap, (0, dummy_val, dummy))
    
    # Bangun tree: gabung 2 node terkecil sampai tersisa 1
    counter = 256  # Tie-breaker untuk internal nodes
    while len(heap) > 1:
        freq1, _, left = heapq.heappop(heap)
        freq2, _, right = heapq.heappop(heap)
        
        # Internal node: frekuensi = sum child
        merged = HuffmanNode(frequency=freq1 + freq2, left=left, right=right)
        heapq.heappush(heap, (merged.frequency, counter, merged))
        counter += 1
    
    # Node terakhir = root
    _, _, root = heap[0]
    return root


def generate_codes(root):
    """
    Langkah 3: Generate kode biner untuk setiap byte dengan traverse tree.
    
    Aturan:
    - Ke kiri = tambah bit '0'
    - Ke kanan = tambah bit '1'
    - Leaf node = simpan kode yang sudah terkumpul
    
    Contoh tree:
           (root)
          /      \\
        (*)      'A'=01
       /   \\
     'B'=00  'C'=10
    
    Hasil: {'A': '1', 'B': '00', 'C': '01'}
    Byte yang lebih sering muncul akan punya kode lebih pendek.
    
    Args:
        root (HuffmanNode): Root dari Huffman Tree
    
    Returns:
        dict: Mapping {byte_value: binary_string}
              Contoh: {65: '1', 66: '00', 67: '01'}
    """
    if root is None:
        return {}
    
    codes = {}
    
    def _traverse(node, current_code):
        """Recursive traversal untuk generate kode."""
        if node.is_leaf():
            # Leaf node: simpan kode. Jika root adalah leaf (1 simbol), kode = '0'
            codes[node.byte_value] = current_code if current_code else '0'
            return
        
        # Traverse ke kiri (bit '0') dan kanan (bit '1')
        if node.left:
            _traverse(node.left, current_code + '0')
        if node.right:
            _traverse(node.right, current_code + '1')
    
    _traverse(root, '')
    return codes


def encode(data):
    """
    ENCODE: Kompresi data menggunakan Huffman Coding.
    
    Proses lengkap:
    1. Hitung frekuensi byte
    2. Bangun Huffman Tree
    3. Generate kode biner
    4. Ganti setiap byte dengan kode Huffman-nya
    5. Konversi bitstring ke bytes (dengan padding)
    6. Pack semua ke format .mvault
    
    Args:
        data (bytes): Data mentah yang akan dikompresi
    
    Returns:
        bytes: Data terkompresi dalam format .mvault
        
    Raises:
        ValueError: Jika data kosong
    """
    if not data:
        raise ValueError("Cannot encode empty data")
    
    # ── Langkah 1-3: Hitung frekuensi → Tree → Kode ──
    freq_table = count_frequencies(data)
    tree = build_huffman_tree(freq_table)
    codes = generate_codes(tree)
    
    # ── Langkah 4: Encode setiap byte menjadi bitstring ──
    # Contoh: b'AABBC' dengan codes {A:'0', B:'10', C:'11'}
    #         → '0' + '0' + '10' + '10' + '11' = '001010011'
    encoded_bits = []
    for byte in data:
        encoded_bits.append(codes[byte])
    bitstring = ''.join(encoded_bits)
    
    # ── Langkah 5: Konversi bitstring ke bytes ──
    # Bitstring harus kelipatan 8 untuk jadi bytes
    # Tambahkan padding bits di akhir
    padding = (8 - len(bitstring) % 8) % 8
    bitstring += '0' * padding  # Padding dengan '0'
    
    # Konversi setiap 8 bit menjadi 1 byte
    encoded_bytes = bytearray()
    for i in range(0, len(bitstring), 8):
        byte = int(bitstring[i:i+8], 2)
        encoded_bytes.append(byte)
    
    # ── Langkah 6: Pack ke format .mvault ──
    result = bytearray()
    
    # Magic number "HVLT" (4 bytes) — identifikasi format
    result.extend(b'HVLT')
    
    # Panjang data asli (4 bytes, unsigned int, big-endian)
    result.extend(struct.pack('>I', len(data)))
    
    # Jumlah simbol unik (2 bytes, unsigned short)
    num_symbols = len(freq_table)
    result.extend(struct.pack('>H', num_symbols))
    
    # Frequency table: [byte (1B)] [frequency (4B)] × num_symbols
    for byte_val, freq in freq_table.items():
        result.append(byte_val)                        # 1 byte: simbol
        result.extend(struct.pack('>I', freq))         # 4 bytes: frekuensi
    
    # Padding bits count (1 byte)
    result.append(padding)
    
    # Encoded bitstream
    result.extend(encoded_bytes)
    
    return bytes(result)


def decode(compressed_data):
    """
    DECODE: Dekompresi data dari format .mvault kembali ke data asli.
    
    Proses:
    1. Baca header: magic number, panjang asli, jumlah simbol
    2. Baca frequency table
    3. Rebuild Huffman Tree dari frequency table
    4. Baca encoded bitstream
    5. Traverse tree mengikuti setiap bit → rekonstruksi data asli
    
    Args:
        compressed_data (bytes): Data terkompresi dalam format .mvault
    
    Returns:
        bytes: Data asli yang sudah di-dekompresi
        
    Raises:
        ValueError: Jika format file tidak valid
    """
    if len(compressed_data) < 10:
        raise ValueError("Compressed data too small — file might be corrupted")
    
    pos = 0  # Posisi baca saat ini
    
    # ── Langkah 1: Baca header ──
    # Magic number (4 bytes)
    magic = compressed_data[pos:pos+4]
    pos += 4
    if magic != b'HVLT':
        raise ValueError(f"Invalid file format. Expected 'HVLT' header, got '{magic}'")
    
    # Panjang data asli (4 bytes)
    original_length = struct.unpack('>I', compressed_data[pos:pos+4])[0]
    pos += 4
    
    # Jumlah simbol unik (2 bytes)
    num_symbols = struct.unpack('>H', compressed_data[pos:pos+2])[0]
    pos += 2
    
    # ── Langkah 2: Baca frequency table ──
    freq_table = {}
    for _ in range(num_symbols):
        byte_val = compressed_data[pos]
        pos += 1
        freq = struct.unpack('>I', compressed_data[pos:pos+4])[0]
        pos += 4
        freq_table[byte_val] = freq
    
    # ── Langkah 3: Rebuild Huffman Tree ──
    tree = build_huffman_tree(freq_table)
    
    # Padding bits count (1 byte)
    padding = compressed_data[pos]
    pos += 1
    
    # ── Langkah 4: Baca encoded bitstream ──
    encoded_bytes = compressed_data[pos:]
    
    # Konversi bytes kembali ke bitstring
    bitstring = ''.join(f'{byte:08b}' for byte in encoded_bytes)
    
    # Hapus padding bits dari akhir
    if padding > 0:
        bitstring = bitstring[:-padding]
    
    # ── Langkah 5: Decode — traverse tree mengikuti setiap bit ──
    decoded = bytearray()
    current_node = tree
    
    for bit in bitstring:
        # Ikuti bit: '0' = kiri, '1' = kanan
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right
        
        # Jika sampai di leaf, output byte dan kembali ke root
        if current_node.is_leaf():
            decoded.append(current_node.byte_value)
            current_node = tree
            
            # Berhenti jika sudah mencapai panjang data asli
            if len(decoded) == original_length:
                break
    
    return bytes(decoded)
