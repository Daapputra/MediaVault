"""
test_image_codec.py — Tests untuk Image Compression/Decompression

Memverifikasi:
1. Kompresi menghasilkan file .mvault yang valid
2. Dekompresi mengembalikan image yang IDENTIK pixel-by-pixel
3. Statistik akurat (ukuran, rasio kompresi)
4. Berbagai mode image (RGB, RGBA, L/grayscale)
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from PIL import Image
from modules.compression.image_codec import compress_image, decompress_image

# Folder temporary untuk test files
TEST_DIR = os.path.join(os.path.dirname(__file__), 'test_data')
os.makedirs(TEST_DIR, exist_ok=True)
os.makedirs(os.path.join(TEST_DIR.replace('tests', 'uploads'), 'output'), exist_ok=True)


def create_test_image(width, height, mode='RGB', color=None, path=None):
    """Helper: buat image test dengan ukuran dan warna tertentu."""
    if color is None:
        if mode == 'RGB':
            color = (255, 0, 0)  # Merah
        elif mode == 'RGBA':
            color = (255, 0, 0, 255)
        elif mode == 'L':
            color = 128
    
    img = Image.new(mode, (width, height), color)
    
    if path is None:
        path = os.path.join(TEST_DIR, f'test_{mode}_{width}x{height}.png')
    
    img.save(path, format='PNG')
    return path


class TestImageCompression:
    """Test image compression."""
    
    def test_compress_rgb(self):
        """Kompresi image RGB harus berhasil dan menghasilkan file .mvault."""
        img_path = create_test_image(100, 100, 'RGB')
        result = compress_image(img_path)
        
        assert os.path.exists(result['output_path'])
        assert result['output_path'].endswith('.mvault')
        assert result['compression_ratio'] > 0  # Harus ada kompresi
        assert result['width'] == 100
        assert result['height'] == 100
        assert result['mode'] == 'RGB'
    
    def test_compress_rgba(self):
        """Kompresi image RGBA."""
        img_path = create_test_image(50, 50, 'RGBA')
        result = compress_image(img_path)
        
        assert os.path.exists(result['output_path'])
        assert result['mode'] == 'RGBA'
    
    def test_compress_grayscale(self):
        """Kompresi image grayscale."""
        img_path = create_test_image(50, 50, 'L')
        result = compress_image(img_path)
        
        assert os.path.exists(result['output_path'])
        assert result['mode'] == 'L'
    
    def test_compression_stats(self):
        """Statistik kompresi harus akurat."""
        img_path = create_test_image(100, 100, 'RGB')
        result = compress_image(img_path)
        
        assert result['original_size'] > 0
        assert result['compressed_size'] > 0
        assert result['processing_time'] > 0
        assert isinstance(result['compression_ratio'], float)


class TestImageDecompression:
    """Test image decompression."""
    
    def test_decompress_rgb(self):
        """Dekompresi image RGB harus menghasilkan PNG."""
        img_path = create_test_image(100, 100, 'RGB')
        comp_result = compress_image(img_path)
        decomp_result = decompress_image(comp_result['output_path'])
        
        assert os.path.exists(decomp_result['output_path'])
        assert decomp_result['output_path'].endswith('.png')
    
    def test_decompress_preserves_dimensions(self):
        """Dimensi image harus sama setelah roundtrip."""
        img_path = create_test_image(200, 150, 'RGB')
        comp_result = compress_image(img_path)
        decomp_result = decompress_image(comp_result['output_path'])
        
        assert decomp_result['width'] == 200
        assert decomp_result['height'] == 150


class TestLosslessRoundtrip:
    """Test PALING KRITIKAL: compress → decompress harus IDENTIK pixel-by-pixel."""
    
    def _verify_lossless(self, width, height, mode, color=None):
        """Helper: verifikasi roundtrip lossless untuk image tertentu."""
        img_path = create_test_image(width, height, mode, color)
        
        # Baca pixel data asli
        original_img = Image.open(img_path)
        original_pixels = list(original_img.getdata())
        
        # Compress → Decompress
        comp_result = compress_image(img_path)
        decomp_result = decompress_image(comp_result['output_path'])
        
        # Baca pixel data hasil
        result_img = Image.open(decomp_result['output_path'])
        result_pixels = list(result_img.getdata())
        
        # Bandingkan pixel-by-pixel
        assert len(original_pixels) == len(result_pixels), \
            f"Pixel count mismatch: {len(original_pixels)} vs {len(result_pixels)}"
        
        for i, (orig, res) in enumerate(zip(original_pixels, result_pixels)):
            assert orig == res, \
                f"LOSSLESS FAILED at pixel {i}: original={orig}, result={res}"
    
    def test_lossless_rgb_red(self):
        """Roundtrip lossless: image merah 100x100."""
        self._verify_lossless(100, 100, 'RGB', (255, 0, 0))
    
    def test_lossless_rgb_gradient(self):
        """Roundtrip lossless: image dengan gradient (variasi warna)."""
        # Buat image dengan gradient horizontal
        img = Image.new('RGB', (100, 50))
        for x in range(100):
            for y in range(50):
                img.putpixel((x, y), (x * 2, y * 4, (x + y) % 256))
        
        path = os.path.join(TEST_DIR, 'test_gradient.png')
        img.save(path, format='PNG')
        
        original_pixels = list(img.getdata())
        
        comp_result = compress_image(path)
        decomp_result = decompress_image(comp_result['output_path'])
        
        result_img = Image.open(decomp_result['output_path'])
        result_pixels = list(result_img.getdata())
        
        assert original_pixels == result_pixels, "LOSSLESS FAILED for gradient image"
    
    def test_lossless_rgba(self):
        """Roundtrip lossless: image RGBA."""
        self._verify_lossless(80, 80, 'RGBA', (100, 200, 50, 128))
    
    def test_lossless_grayscale(self):
        """Roundtrip lossless: image grayscale."""
        self._verify_lossless(60, 60, 'L', 42)
    
    def test_lossless_small(self):
        """Roundtrip lossless: image sangat kecil (1x1 pixel)."""
        self._verify_lossless(1, 1, 'RGB', (1, 2, 3))
    
    def test_lossless_nonsquare(self):
        """Roundtrip lossless: image non-square."""
        self._verify_lossless(200, 50, 'RGB', (0, 128, 255))


class TestErrorHandling:
    """Test error handling."""
    
    def test_invalid_image_path(self):
        """Path yang tidak ada harus raise ValueError."""
        with pytest.raises(ValueError):
            compress_image('/nonexistent/path/image.png')
    
    def test_invalid_mvault_file(self):
        """File .mvault dengan format salah harus raise ValueError."""
        # Buat file palsu
        fake_path = os.path.join(TEST_DIR, 'fake.mvault')
        with open(fake_path, 'wb') as f:
            f.write(b'NOT_A_VALID_MVAULT_FILE')
        
        with pytest.raises(ValueError):
            decompress_image(fake_path)


# Cleanup
def teardown_module():
    """Bersihkan file test setelah semua test selesai."""
    import shutil
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR, ignore_errors=True)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
