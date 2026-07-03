# 🔐 Media Vault

**Media Vault** is an advanced, educational-grade Media Processing Hub built as a Capstone Project for the Multimedia Systems course. It features **Lossless Media Compression** and **Secure Steganography** built entirely from scratch without relying on instant third-party libraries for the core algorithms.

## ✨ Core Features

### 1. Lossless Data Compression (Custom Implementation)
- **Huffman Coding:** Implemented from scratch using a Min-Heap Priority Queue. Converts standard files into a custom `.mvault` binary format to reduce file size while preserving 100% of the original data.
- **Run-Length Encoding (RLE):** Secondary compression algorithm for handling data with high repetition rates.
- **Lossless Guarantee:** Images decompressed from `.mvault` files are mathematically identical to the original input.

### 2. Secure Steganography (LSB)
- **Least Significant Bit (LSB):** Hides secret text messages invisibly inside the raw pixel data of images.
- **Capacity Validation:** Automatically calculates the maximum character capacity based on the image resolution and prevents corruption by blocking oversized messages.
- **Strict Format Handling:** Enforces `PNG` (lossless) output to prevent lossy compression (like JPEG) from destroying the hidden data.

## 🛠️ Technology Stack

**Frontend:**
- **React.js** (via Vite)
- **Tailwind CSS v3** (Custom Dark Mode UI / Glassmorphism)
- **Recharts** (Interactive Statistics)
- **Lucide React** (Icons)

**Backend:**
- **Python 3 / Flask** (REST API)
- **Pillow (PIL)** (Extracting raw pixel data, NOT for compression)
- **Pytest** (Automated Unit Testing & Lossless Verification)

## 🚀 Cara Menjalankan Project (Untuk Teman Kelompok)

Ikuti langkah-langkah di bawah ini secara berurutan agar aplikasi berjalan lancar di komputer masing-masing.

### 0. Clone Repository
Buka terminal/CMD dan jalankan:
```bash
git clone https://github.com/Daapputra/MediaVault.git
cd MediaVault
```

### 1. Setup Backend (Python)
Buka terminal baru, masuk ke folder `backend`, dan buat Virtual Environment agar library tidak berantakan:
```bash
cd backend
python -m venv venv
```
Aktifkan Virtual Environment:
- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

Setelah venv aktif (ada tulisan `(venv)` di terminal), install dependencies:
```bash
pip install -r requirements.txt
```
Lalu jalankan server backend:
```bash
python app.py
```
*(Biarkan terminal ini tetap terbuka. Backend berjalan di `http://localhost:5000`)*

### 2. Setup Frontend (React/Vite)
Buka **terminal baru** (biarkan terminal backend di atas tetap jalan), masuk ke folder `frontend`:
```bash
cd frontend
npm install
```
Jalankan server frontend:
```bash
npm run dev
```
*(Frontend berjalan di `http://localhost:5173`. Buka link ini di browser Anda!)*

---

## 🧪 Automated Testing

The backend includes a comprehensive suite of unit tests to mathematically prove the integrity of the compression and steganography algorithms.

To run the test suite (pastikan venv backend sedang aktif):
```bash
cd backend
python -m pytest tests/ -v
```

## 🏗️ Project Roadmap

- [x] **Phase 1:** Foundation & Image Module (Huffman Codec & LSB Steganography)
- [x] **Phase 2:** Audio Module (WAV Compression & Steganography)
- [x] **Phase 3:** Video Module (Huffman Archive & EOF Structural Steganography)
- [x] **Phase 4:** Final UI Polish & Bug Fixing

---
*Developed for Multimedia Systems Capstone Project*
