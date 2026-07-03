import React, { useState } from 'react';
import { EyeOff, Eye, RefreshCw } from 'lucide-react';
import FileUploader from '../ui/FileUploader';
import Button from '../ui/Button';
import ProgressBar from '../ui/ProgressBar';
import ResultCard from '../ui/ResultCard';
import MediaPreview from '../ui/MediaPreview';
import { embedAudioMessage, extractAudioMessage } from '../../services/api';

const AudioSteganography = () => {
  const [mode, setMode] = useState('embed'); // 'embed' or 'extract'
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
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
    if (mode === 'embed' && !message.trim()) {
      setError('Please enter a message to hide.');
      return;
    }
    
    setIsProcessing(true);
    setError('');
    setProgress(0);
    setResult(null);

    try {
      const response = mode === 'embed' 
        ? await embedAudioMessage(file, message, setProgress)
        : await extractAudioMessage(file, setProgress);
        
      setResult(response.data);
    } catch (err) {
      setError(err.message || 'An error occurred during processing.');
    } finally {
      setIsProcessing(false);
    }
  };

  const reset = () => {
    setFile(null);
    setMessage('');
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
            mode === 'embed' 
              ? 'bg-secondary text-background shadow-md shadow-secondary/20' 
              : 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'
          }`}
          onClick={() => { setMode('embed'); reset(); }}
        >
          <EyeOff className="w-4 h-4" /> Embed Message
        </button>
        <button
          className={`flex items-center gap-2 px-6 py-2 rounded-lg font-medium transition-colors ${
            mode === 'extract' 
              ? 'bg-secondary text-background shadow-md shadow-secondary/20' 
              : 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'
          }`}
          onClick={() => { setMode('extract'); reset(); }}
        >
          <Eye className="w-4 h-4" /> Extract Message
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Upload & Controls */}
        <div className="space-y-6">
          <div className="glass-panel p-6">
            <h2 className="text-xl font-semibold text-text-primary mb-4">
              {mode === 'embed' ? 'Upload Cover Audio (.wav)' : 'Upload Stego Audio (.wav)'}
            </h2>
            
            <FileUploader 
              onFileSelect={handleFileSelect}
              accept="audio/wav"
              fileType="audio"
            />
            
            <p className="text-xs text-text-secondary mt-2">
              Note: Only supports lossless .wav files. Lossy formats (like .mp3) would destroy the hidden message.
            </p>

            {mode === 'embed' && (
              <div className="mt-6">
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Secret Message
                </label>
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Enter the secret message you want to hide in the audio..."
                  className="w-full h-32 px-4 py-3 bg-background border border-border rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent resize-none placeholder-text-secondary/50"
                />
                <div className="text-right mt-1">
                  <span className="text-xs text-text-secondary">
                    {message.length} characters
                  </span>
                </div>
              </div>
            )}

            {error && (
              <div className="mt-4 p-4 bg-error/10 border border-error/20 rounded-lg text-error text-sm">
                {error}
              </div>
            )}

            <div className="mt-6">
              <Button 
                onClick={processFile} 
                disabled={!file || (mode === 'embed' && !message) || isProcessing}
                isLoading={isProcessing}
                variant="secondary"
                className="w-full"
              >
                {mode === 'embed' ? 'Hide Message (LSB)' : 'Extract Secret Message'}
              </Button>
            </div>

            {isProcessing && (
              <div className="mt-6">
                <ProgressBar progress={progress} label={progress < 100 ? "Uploading..." : "Processing..."} isIndeterminate={progress >= 100} />
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Preview & Results */}
        <div className="space-y-6 flex flex-col">
          {mode === 'embed' && file && !result && (
            <div className="glass-panel p-6 flex-1 flex flex-col justify-center items-center">
              <h3 className="text-lg font-medium text-text-primary mb-4 self-start">Cover Audio Preview</h3>
              <div className="w-full max-w-sm">
                <MediaPreview file={file} type="audio" className="w-full" />
              </div>
            </div>
          )}

          {result && (
            <div className="animate-fade-in-up">
              <ResultCard 
                result={result} 
                type={mode === 'embed' ? 'stego_embed' : 'stego_extract'} 
                title={mode === 'embed' ? "Message Embedded!" : "Message Extracted!"}
              />
            </div>
          )}

          {result && (
            <div className="flex justify-end mt-4">
               <Button onClick={reset} variant="ghost" icon={RefreshCw}>
                 Start Over
               </Button>
            </div>
          )}
          
          {!result && mode === 'extract' && (
            <div className="glass-panel p-6 bg-secondary/5 border-secondary/20 h-full flex flex-col justify-center">
              <h3 className="font-semibold text-text-primary mb-2 flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-secondary/20 flex items-center justify-center text-secondary text-xs font-bold">i</span>
                Extraction Info
              </h3>
              <p className="text-sm text-text-secondary leading-relaxed">
                Upload a .wav file that previously had a message embedded using this system. The algorithm will read the Least Significant Bits of the audio frames to reconstruct your exact original message.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AudioSteganography;
