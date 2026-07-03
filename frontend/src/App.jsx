import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import ImageCompression from './components/compression/ImageCompression';
import AudioCompression from './components/compression/AudioCompression';
import VideoCompression from './components/compression/VideoCompression';
import ImageSteganography from './components/steganography/ImageSteganography';
import AudioSteganography from './components/steganography/AudioSteganography';
import VideoSteganography from './components/steganography/VideoSteganography';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          
          {/* Compression Routes */}
          <Route path="compression/image" element={<ImageCompression />} />
          <Route path="compression/audio" element={<AudioCompression />} />
          <Route path="compression/video" element={<VideoCompression />} />
          
          {/* Steganography Routes */}
          <Route path="steganography/image" element={<ImageSteganography />} />
          <Route path="steganography/audio" element={<AudioSteganography />} />
          <Route path="steganography/video" element={<VideoSteganography />} />
          
          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
