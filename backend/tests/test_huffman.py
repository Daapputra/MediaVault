"""
test_huffman.py — Unit tests untuk Huffman Coding

Memverifikasi:
1. Encode → Decode menghasilkan data identik (lossless)
2. Data terkompresi lebih kecil dari data asli (untuk data yang bisa dikompresi)
3. Edge cases: data 1 byte, semua byte sama, data random
4. Format file (.mvault) valid
"""

import os
import sys
import random

# Setup path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from modules.compression.huffman import (
    count_frequencies, build_huffman_tree, generate_codes,
    encode, decode, HuffmanNode
)


class TestCountFrequencies:
    """Test fungsi count_frequencies."""
    
    def test_simple_string(self):
        """Frekuensi harus benar untuk string sederhana."""
        data = b'AABBBC'
        freq = count_frequencies(data)
        assert freq[65] == 2   # 'A' = 65
        assert freq[66] == 3   # 'B' = 66
        assert freq[67] == 1   # 'C' = 67
    
    def test_single_byte(self):
        """Data dengan 1 byte saja."""
        data = b'A'
        freq = count_frequencies(data)
        assert freq[65] == 1
        assert len(freq) == 1
    
    def test_all_same(self):
        """Semua byte sama — hanya 1 entry di frequency table."""
        data = b'AAAAAAA'
        freq = count_frequencies(data)
        assert len(freq) == 1
        assert freq[65] == 7


class TestBuildTree:
    """Test fungsi build_huffman_tree."""
    
    def test_tree_root_frequency(self):
        """Root frequency harus = total semua byte."""
        freq = {65: 5, 66: 3, 67: 2}
        tree = build_huffman_tree(freq)
        assert tree.frequency == 10
    
    def test_single_symbol(self):
        """Tree dengan 1 simbol harus tetap valid."""
        freq = {65: 10}
        tree = build_huffman_tree(freq)
        assert tree is not None
    
    def test_empty(self):
        """Frequency table kosong → tree None."""
        tree = build_huffman_tree({})
        assert tree is None


class TestGenerateCodes:
    """Test fungsi generate_codes."""
    
    def test_codes_are_unique(self):
        """Setiap simbol harus punya kode unik."""
        freq = {65: 5, 66: 3, 67: 2, 68: 1}
        tree = build_huffman_tree(freq)
        codes = generate_codes(tree)
        
        # Semua kode harus berbeda
        code_values = list(codes.values())
        assert len(code_values) == len(set(code_values))
    
    def test_prefix_free(self):
        """Kode Huffman harus prefix-free (tidak ada kode yang menjadi prefix kode lain)."""
        freq = {65: 5, 66: 3, 67: 2, 68: 1}
        tree = build_huffman_tree(freq)
        codes = generate_codes(tree)
        
        code_list = sorted(codes.values())
        for i in range(len(code_list)):
            for j in range(i + 1, len(code_list)):
                assert not code_list[j].startswith(code_list[i]), \
                    f"Code '{code_list[i]}' is prefix of '{code_list[j]}'"
    
    def test_frequent_bytes_shorter_code(self):
        """Byte yang lebih sering muncul seharusnya punya kode lebih pendek (atau sama)."""
        freq = {65: 100, 66: 1}  # 'A' sangat sering, 'B' jarang
        tree = build_huffman_tree(freq)
        codes = generate_codes(tree)
        
        assert len(codes[65]) <= len(codes[66])


class TestEncodeDecodeRoundtrip:
    """Test PALING PENTING: encode → decode harus menghasilkan data identik."""
    
    def test_simple_text(self):
        """Teks sederhana."""
        original = b'Hello, World! This is a test of Huffman coding.'
        compressed = encode(original)
        decompressed = decode(compressed)
        assert decompressed == original, "LOSSLESS FAILED: decompressed != original"
    
    def test_binary_data(self):
        """Data biner (semua nilai byte 0-255)."""
        original = bytes(range(256))
        compressed = encode(original)
        decompressed = decode(compressed)
        assert decompressed == original
    
    def test_repeated_data(self):
        """Data dengan banyak pengulangan (ideal untuk kompresi)."""
        original = b'A' * 1000 + b'B' * 500 + b'C' * 100
        compressed = encode(original)
        decompressed = decode(compressed)
        assert decompressed == original
    
    def test_single_byte(self):
        """Edge case: data hanya 1 byte."""
        original = b'X'
        compressed = encode(original)
        decompressed = decode(compressed)
        assert decompressed == original
    
    def test_all_same_bytes(self):
        """Edge case: semua byte identik."""
        original = b'\x42' * 500
        compressed = encode(original)
        decompressed = decode(compressed)
        assert decompressed == original
    
    def test_random_data(self):
        """Data random — worst case untuk kompresi tapi harus tetap lossless."""
        random.seed(42)  # Reproducible
        original = bytes(random.randint(0, 255) for _ in range(5000))
        compressed = encode(original)
        decompressed = decode(compressed)
        assert decompressed == original
    
    def test_large_data(self):
        """Data besar (100KB) — stress test."""
        random.seed(123)
        original = bytes(random.randint(0, 255) for _ in range(100_000))
        compressed = encode(original)
        decompressed = decode(compressed)
        assert decompressed == original
    
    def test_two_symbols(self):
        """Hanya 2 simbol unik."""
        original = b'\x00\x01' * 100
        compressed = encode(original)
        decompressed = decode(compressed)
        assert decompressed == original


class TestCompression:
    """Test bahwa data terkompresi benar-benar lebih kecil."""
    
    def test_repeated_data_compresses(self):
        """Data berulang harus menghasilkan output lebih kecil dari raw data."""
        original = b'A' * 1000
        compressed = encode(original)
        # Compressed harus lebih kecil dari original
        assert len(compressed) < len(original), \
            f"Compression failed: {len(compressed)} >= {len(original)}"
    
    def test_text_compresses(self):
        """Teks natural biasanya bisa dikompresi."""
        original = b'The quick brown fox jumps over the lazy dog. ' * 20
        compressed = encode(original)
        assert len(compressed) < len(original)


class TestErrorHandling:
    """Test error handling."""
    
    def test_empty_data(self):
        """Data kosong harus raise ValueError."""
        with pytest.raises(ValueError, match="Cannot encode empty data"):
            encode(b'')
    
    def test_invalid_format(self):
        """Data dengan header salah harus raise ValueError."""
        with pytest.raises(ValueError):
            decode(b'INVALID_DATA_HERE_LONG_ENOUGH')
    
    def test_truncated_data(self):
        """Data terpotong harus raise ValueError."""
        with pytest.raises(ValueError):
            decode(b'HVLT')  # Header only, no content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
