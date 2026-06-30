import React, { useState } from 'react';
import { RefreshCw, Minimize2, Maximize2 } from 'lucide-react';
import FileUploader from '../ui/FileUploader';
import Button from '../ui/Button';
import ProgressBar from '../ui/ProgressBar';
import ResultCard from '../ui/ResultCard';
import MediaPreview from '../ui/MediaPreview';
import { compressImage, decompressImage } from '../../services/api';

const ImageCompression = () => {
  const [mode, setMode] = useState('compress'); // 'compress' or 'decompress'
  const [file, setFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile);
    setResult(null);
    setError('');
  };

  const processFile = async () => {
    if (!file) return;
    
    setIsProcessing(true);
    setError('');
    setProgress(0);
    setResult(null);

    try {
      const response = mode === 'compress' 
        ? await compressImage(file, setProgress)
        : await decompressImage(file, setProgress);
        
      setResult(response.data);
    } catch (err) {
      setError(err.message || 'An error occurred during processing.');
    } finally {
      setIsProcessing(false);
    }
  };

  const reset = () => {
    setFile(null);
    setResult(null);
    setError('');
    setProgress(0);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
      {/* Mode Switcher */}
      <div className="flex bg-surface p-1 rounded-xl w-fit border border-border">
        <button
          className={`flex items-center gap-2 px-6 py-2 rounded-lg font-medium transition-colors ${
            mode === 'compress' 
              ? 'bg-primary text-white shadow-md shadow-primary/20' 
              : 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'
          }`}
          onClick={() => { setMode('compress'); reset(); }}
        >
          <Minimize2 className="w-4 h-4" /> Compress
        </button>
        <button
          className={`flex items-center gap-2 px-6 py-2 rounded-lg font-medium transition-colors ${
            mode === 'decompress' 
              ? 'bg-primary text-white shadow-md shadow-primary/20' 
              : 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'
          }`}
          onClick={() => { setMode('decompress'); reset(); }}
        >
          <Maximize2 className="w-4 h-4" /> Decompress
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Upload & Controls */}
        <div className="space-y-6">
          <div className="glass-panel p-6">
            <h2 className="text-xl font-semibold text-text-primary mb-4">
              {mode === 'compress' ? 'Upload Image' : 'Upload .mvault File'}
            </h2>
            
            <FileUploader 
              onFileSelect={handleFileSelect}
              accept={mode === 'compress' ? 'image/png,image/jpeg,image/bmp' : '.mvault'}
              fileType={mode === 'compress' ? 'image' : 'file'}
            />

            {error && (
              <div className="mt-4 p-4 bg-error/10 border border-error/20 rounded-lg text-error text-sm">
                {error}
              </div>
            )}

            <div className="mt-6">
              <Button 
                onClick={processFile} 
                disabled={!file || isProcessing}
                isLoading={isProcessing}
                className="w-full"
              >
                {mode === 'compress' ? 'Compress Image (Lossless)' : 'Decompress Image'}
              </Button>
            </div>

            {isProcessing && (
              <div className="mt-6">
                <ProgressBar progress={progress} label={progress < 100 ? "Uploading..." : "Processing (this may take a moment)..."} isIndeterminate={progress >= 100} />
              </div>
            )}
          </div>
          
          {/* Info Card */}
          <div className="glass-panel p-6 bg-primary/5 border-primary/20">
            <h3 className="font-semibold text-text-primary mb-2 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center text-primary text-xs font-bold">i</span>
              How it works
            </h3>
            <p className="text-sm text-text-secondary leading-relaxed">
              {mode === 'compress' 
                ? "This uses a custom implementation of Huffman Coding to compress raw pixel data. It is 100% lossless, meaning the decompressed image will be mathematically identical to the original."
                : "Upload a previously compressed .mvault file. The system will decode the Huffman tree and reconstruct the exact original image in PNG format."}
            </p>
          </div>
        </div>

        {/* Right Column: Preview & Results */}
        <div className="space-y-6 flex flex-col">
          {mode === 'compress' && file && !result && (
            <div className="glass-panel p-6 flex-1 flex flex-col">
              <h3 className="text-lg font-medium text-text-primary mb-4">Original Image Preview</h3>
              <MediaPreview file={file} type="image" className="flex-1" />
            </div>
          )}

          {result && (
            <div className="animate-fade-in-up">
              <ResultCard 
                result={result} 
                type={mode} 
                title={mode === 'compress' ? "Compression Successful!" : "Decompression Successful!"}
              />
            </div>
          )}

          {mode === 'compress' && result && (
            <div className="flex justify-end mt-4">
               <Button onClick={reset} variant="ghost" icon={RefreshCw}>
                 Start Over
               </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImageCompression;
