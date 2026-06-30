import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import ImageCompression from './components/compression/ImageCompression';
import ImageSteganography from './components/steganography/ImageSteganography';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          
          {/* Compression Routes */}
          <Route path="compression/image" element={<ImageCompression />} />
          <Route path="compression/audio" element={<div className="p-8 text-center text-text-secondary glass-panel">Audio Compression coming soon in Phase 2</div>} />
          <Route path="compression/video" element={<div className="p-8 text-center text-text-secondary glass-panel">Video Compression coming soon in Phase 3</div>} />
          
          {/* Steganography Routes */}
          <Route path="steganography/image" element={<ImageSteganography />} />
          <Route path="steganography/audio" element={<div className="p-8 text-center text-text-secondary glass-panel">Audio Steganography coming soon in Phase 2</div>} />
          <Route path="steganography/video" element={<div className="p-8 text-center text-text-secondary glass-panel">Video Steganography coming soon in Phase 3</div>} />
          
          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
