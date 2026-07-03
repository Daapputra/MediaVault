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

## 🚀 How to Run Locally

### 1. Backend Setup
Navigate to the backend directory and install the requirements:
```bash
cd backend
pip install -r requirements.txt
```
Start the Flask API server:
```bash
python app.py
```
*The backend will run on `http://localhost:5000`*

### 2. Frontend Setup
Open a new terminal, navigate to the frontend directory, and install dependencies:
```bash
cd frontend
npm install
```
Start the Vite development server:
```bash
npm run dev
```
*The frontend will run on `http://localhost:5173`*

## 🧪 Automated Testing

The backend includes a comprehensive suite of 52 unit tests to mathematically prove the integrity of the compression and steganography algorithms.

To run the test suite:
```bash
cd backend
pytest tests/ -v
```

## 🏗️ Project Roadmap

- [x] **Phase 1:** Foundation & Image Module (Huffman Codec & LSB Steganography)
- [ ] **Phase 2:** Audio Module (WAV Compression & Steganography) - *In Progress*
- [ ] **Phase 3:** Video Module (AVI/MP4 Frame-by-Frame Processing)
- [ ] **Phase 4:** Final UI Polish & Edge Case Handling

---
*Developed for Multimedia Systems Capstone Project*
