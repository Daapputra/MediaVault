import React, { useState, useEffect } from 'react';
import { Image as ImageIcon, Music, Video, AlertCircle } from 'lucide-react';

const MediaPreview = ({ file, type = 'image', url = null, className = '' }) => {
  const [previewUrl, setPreviewUrl] = useState(url);
  const [error, setError] = useState(false);

  useEffect(() => {
    // If it's a File object and no external URL is provided, create object URL
    if (file && !url) {
      const objectUrl = URL.createObjectURL(file);
      setPreviewUrl(objectUrl);
      
      return () => {
        URL.revokeObjectURL(objectUrl);
      };
    } else if (url) {
      setPreviewUrl(url);
    }
  }, [file, url]);

  if (error) {
    return (
      <div className={`flex flex-col items-center justify-center p-6 bg-surface border border-border rounded-xl ${className}`}>
        <AlertCircle className="w-10 h-10 text-error mb-2" />
        <p className="text-sm text-text-secondary text-center">Preview not available</p>
      </div>
    );
  }

  if (!previewUrl) {
    return (
      <div className={`flex flex-col items-center justify-center p-6 bg-surface border border-border rounded-xl ${className}`}>
        {type === 'image' && <ImageIcon className="w-10 h-10 text-text-secondary mb-2" />}
        {type === 'audio' && <Music className="w-10 h-10 text-text-secondary mb-2" />}
        {type === 'video' && <Video className="w-10 h-10 text-text-secondary mb-2" />}
        <p className="text-sm text-text-secondary text-center">No preview available</p>
      </div>
    );
  }

  return (
    <div className={`relative rounded-xl overflow-hidden bg-surface border border-border flex items-center justify-center ${className}`}>
      {type === 'image' && (
        <img 
          src={previewUrl} 
          alt="Preview" 
          className="max-w-full max-h-[300px] object-contain"
          onError={() => setError(true)}
        />
      )}
      
      {type === 'audio' && (
        <div className="w-full p-4">
          <audio 
            src={previewUrl} 
            controls 
            className="w-full"
            onError={() => setError(true)}
          />
        </div>
      )}
      
      {type === 'video' && (
        <video 
          src={previewUrl} 
          controls 
          className="max-w-full max-h-[300px]"
          onError={() => setError(true)}
        />
      )}
    </div>
  );
};

export default MediaPreview;
