import React, { useCallback, useState, useRef } from 'react';
import { UploadCloud, File, X, Image as ImageIcon, Music, Video } from 'lucide-react';

const FileUploader = ({ onFileSelect, accept = "*", maxMB = 20, fileType = 'image' }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState('');
  const inputRef = useRef(null);

  const getIcon = () => {
    switch (fileType) {
      case 'image': return <ImageIcon className="w-10 h-10 text-primary mb-3" />;
      case 'audio': return <Music className="w-10 h-10 text-primary mb-3" />;
      case 'video': return <Video className="w-10 h-10 text-primary mb-3" />;
      default: return <UploadCloud className="w-10 h-10 text-primary mb-3" />;
    }
  };

  const validateFile = (file) => {
    setError('');
    
    // Size check
    const sizeMB = file.size / (1024 * 1024);
    if (sizeMB > maxMB) {
      setError(`File is too large (${sizeMB.toFixed(1)} MB). Maximum allowed is ${maxMB} MB.`);
      return false;
    }

    return true;
  };

  const handleFile = (file) => {
    if (file && validateFile(file)) {
      setSelectedFile(file);
      if (onFileSelect) onFileSelect(file);
    }
  };

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const clearFile = (e) => {
    e.stopPropagation();
    setSelectedFile(null);
    setError('');
    if (inputRef.current) inputRef.current.value = '';
    if (onFileSelect) onFileSelect(null);
  };

  return (
    <div className="w-full">
      {!selectedFile ? (
        <div
          className={`relative w-full h-64 border-2 border-dashed rounded-xl flex flex-col items-center justify-center p-6 transition-colors duration-200 cursor-pointer overflow-hidden
            ${dragActive ? 'border-primary bg-primary/10' : 'border-border bg-surface hover:bg-surface-hover hover:border-primary/50'}
            ${error ? 'border-error/50 bg-error/5' : ''}
          `}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            className="hidden"
            accept={accept}
            onChange={handleChange}
          />
          
          <div className="flex flex-col items-center text-center pointer-events-none z-10">
            {getIcon()}
            <p className="text-lg font-semibold text-text-primary mb-1">
              Drag & Drop your file here
            </p>
            <p className="text-sm text-text-secondary mb-4">
              or click to browse from your computer
            </p>
            
            <div className="inline-block bg-background px-4 py-1.5 rounded-full text-xs text-text-secondary border border-border">
              Supported: {accept} • Max size: {maxMB}MB
            </div>
          </div>
          
          {/* Animated background rings */}
          <div className="absolute inset-0 pointer-events-none flex items-center justify-center opacity-20">
            <div className={`w-32 h-32 rounded-full border border-primary transition-transform duration-700 ease-out ${dragActive ? 'scale-150' : 'scale-100'}`}></div>
            <div className={`absolute w-48 h-48 rounded-full border border-primary transition-transform duration-700 delay-75 ease-out ${dragActive ? 'scale-150' : 'scale-100'}`}></div>
          </div>
        </div>
      ) : (
        <div className="glass-panel p-4 flex items-center justify-between group">
          <div className="flex items-center gap-4 truncate">
            <div className="w-12 h-12 bg-primary/20 text-primary rounded-lg flex items-center justify-center shrink-0">
              <File className="w-6 h-6" />
            </div>
            <div className="truncate">
              <p className="font-medium text-text-primary truncate" title={selectedFile.name}>
                {selectedFile.name}
              </p>
              <p className="text-sm text-text-secondary">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
          </div>
          
          <button
            onClick={clearFile}
            className="w-8 h-8 flex items-center justify-center rounded-full bg-surface-hover text-text-secondary hover:text-error hover:bg-error/10 transition-colors"
            title="Remove file"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
      
      {error && (
        <p className="mt-2 text-sm text-error flex items-center gap-1.5">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-error"></span>
          {error}
        </p>
      )}
    </div>
  );
};

export default FileUploader;
