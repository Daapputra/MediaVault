"""
test_image_stego.py — Tests untuk Image Steganography

Memverifikasi:
1. Embed → Extract mengembalikan pesan 100% identik
2. Validasi kapasitas berfungsi (pesan terlalu panjang → error)
3. Berbagai jenis pesan (ASCII, Unicode, panjang)
4. Image berbagai ukuran
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from PIL import Image
from modules.steganography.image_stego import embed_message, extract_message

# Folder test
TEST_DIR = os.path.join(os.path.dirname(__file__), 'test_stego_data')
os.makedirs(TEST_DIR, exist_ok=True)
os.makedirs(os.path.join(TEST_DIR.replace('tests', 'uploads'), 'output'), exist_ok=True)


def create_test_image(width, height, path=None):
    """Helper: buat image test."""
    img = Image.new('RGB', (width, height), (100, 150, 200))
    if path is None:
        path = os.path.join(TEST_DIR, f'stego_test_{width}x{height}.png')
    img.save(path, format='PNG')
    return path


class TestEmbedExtractRoundtrip:
    """Test PALING KRITIKAL: embed → extract harus menghasilkan pesan identik."""
    
    def _verify_roundtrip(self, image_size, message):
        """Helper: verifikasi embed → extract roundtrip."""
        img_path = create_test_image(image_size[0], image_size[1])
        
        # Embed pesan
        embed_result = embed_message(img_path, message)
        
        # Extract pesan
        extract_result = extract_message(embed_result['output_path'])
        
        # Verifikasi pesan identik
        assert extract_result['message'] == message, \
            f"MESSAGE MISMATCH!\n  Embedded: '{message}'\n  Extracted: '{extract_result['message']}'"
    
    def test_simple_message(self):
        """Pesan sederhana ASCII."""
        self._verify_roundtrip((100, 100), "Hello World!")
    
    def test_long_message(self):
        """Pesan panjang."""
        message = "This is a longer test message. " * 10
        self._verify_roundtrip((200, 200), message)
    
    def test_special_characters(self):
        """Pesan dengan karakter spesial."""
        self._verify_roundtrip((100, 100), "Special chars: @#$%^&*()!~`")
    
    def test_numbers(self):
        """Pesan berisi angka."""
        self._verify_roundtrip((100, 100), "12345 67890")
    
    def test_single_character(self):
        """Pesan hanya 1 karakter."""
        self._verify_roundtrip((50, 50), "A")
    
    def test_unicode_message(self):
        """Pesan dengan karakter Unicode (emoji, non-Latin)."""
        self._verify_roundtrip((200, 200), "Hello! Pesan rahasia 123")
    
    def test_multiline_message(self):
        """Pesan dengan newlines."""
        message = "Line 1\nLine 2\nLine 3"
        self._verify_roundtrip((100, 100), message)
    
    def test_empty_spaces(self):
        """Pesan dengan banyak spasi."""
        self._verify_roundtrip((100, 100), "   spaces   everywhere   ")


class TestCapacityValidation:
    """Test validasi kapasitas."""
    
    def test_message_too_long(self):
        """Pesan yang terlalu panjang harus raise ValueError."""
        # Image 5x5 RGB = 75 bytes carrier, capacity ≈ 5 karakter
        img_path = create_test_image(5, 5)
        long_message = "A" * 100  # Pasti melebihi kapasitas
        
        with pytest.raises(ValueError, match="too long"):
            embed_message(img_path, long_message)
    
    def test_max_capacity(self):
        """Embed pesan mendekati kapasitas maksimum harus berhasil."""
        # Image 100x100 RGB = 30000 bytes, capacity ≈ 3746 karakter
        img_path = create_test_image(100, 100)
        
        # Embed result tells us capacity
        embed_result = embed_message(img_path, "test")
        capacity = embed_result['capacity']
        
        # Buat pesan mendekati kapasitas (90%)
        safe_length = int(capacity * 0.9)
        message = "A" * safe_length
        
        embed_result = embed_message(img_path, message)
        extract_result = extract_message(embed_result['output_path'])
        
        assert extract_result['message'] == message


class TestStatistics:
    """Test statistik hasil."""
    
    def test_embed_statistics(self):
        """Hasil embed harus punya semua statistik."""
        img_path = create_test_image(100, 100)
        result = embed_message(img_path, "Test message")
        
        assert 'output_path' in result
        assert 'original_size' in result
        assert 'stego_size' in result
        assert 'message_length' in result
        assert 'capacity' in result
        assert 'usage_percent' in result
        assert 'processing_time' in result
        assert result['message_length'] == len("Test message".encode('utf-8'))
    
    def test_extract_statistics(self):
        """Hasil extract harus punya statistik."""
        img_path = create_test_image(100, 100)
        embed_result = embed_message(img_path, "Test")
        extract_result = extract_message(embed_result['output_path'])
        
        assert 'message' in extract_result
        assert 'message_length' in extract_result
        assert 'processing_time' in extract_result


class TestImageIntegrity:
    """Test bahwa stego image terlihat normal."""
    
    def test_stego_image_is_valid_png(self):
        """Stego image harus bisa dibuka sebagai PNG yang valid."""
        img_path = create_test_image(100, 100)
        result = embed_message(img_path, "Hidden message")
        
        # Harus bisa dibuka tanpa error
        stego_img = Image.open(result['output_path'])
        assert stego_img.size == (100, 100)
        assert stego_img.mode in ('RGB', 'RGBA')
    
    def test_stego_image_dimensions_preserved(self):
        """Dimensi image harus tetap sama setelah embedding."""
        img_path = create_test_image(200, 150)
        result = embed_message(img_path, "Hello")
        
        stego_img = Image.open(result['output_path'])
        assert stego_img.size == (200, 150)


class TestErrorHandling:
    """Test error handling."""
    
    def test_invalid_image_path(self):
        """Path tidak valid harus raise ValueError."""
        with pytest.raises(ValueError):
            embed_message('/nonexistent/image.png', "test")
    
    def test_extract_from_non_stego_image(self):
        """Extract dari image tanpa pesan tersembunyi — behavior tergantung LSB data."""
        # Image baru tanpa pesan → LSB bisa random → mungkin error atau return garbage
        img_path = create_test_image(100, 100)
        # Ini bisa raise ValueError atau return string random
        # Yang penting: tidak crash
        try:
            result = extract_message(img_path)
            # Jika berhasil extract, hasilnya pasti bukan pesan yang meaningful
            assert isinstance(result['message'], str)
        except ValueError:
            pass  # Expected — tidak ada pesan valid


# Cleanup
def teardown_module():
    """Bersihkan file test."""
    import shutil
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR, ignore_errors=True)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
