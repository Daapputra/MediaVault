import React from 'react';
import { Download, Clock, HardDrive, Zap, CheckCircle2 } from 'lucide-react';
import Button from './Button';
import StatsChart from './StatsChart';

const ResultCard = ({ result, title = "Compression Result", type = "compression" }) => {
  if (!result) return null;

  return (
    <div className="glass-panel p-6 w-full animate-fade-in">
      <div className="flex items-center gap-3 mb-6 pb-4 border-b border-border">
        <div className="p-2 bg-success/20 rounded-full text-success">
          <CheckCircle2 className="w-6 h-6" />
        </div>
        <h3 className="text-xl font-semibold text-text-primary">{title}</h3>
      </div>

      {type === 'compression' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <StatItem 
                icon={HardDrive} 
                label="Raw Uncompressed Size" 
                value={result.original_raw_size_formatted} 
                subValue={`${result.original_raw_size} bytes`}
              />
              <StatItem 
                icon={Zap} 
                label="Compressed Size" 
                value={result.compressed_size_formatted} 
                subValue={`${result.compressed_size} bytes`}
                highlight={true}
              />
              <StatItem 
                icon={Clock} 
                label="Time Taken" 
                value={`${result.processing_time}s`} 
              />
              <div className="p-4 bg-surface rounded-lg border border-border">
                <p className="text-sm text-text-secondary mb-1">Ratio</p>
                <p className="text-xl font-bold text-success">
                  {result.compression_ratio}%
                </p>
              </div>
            </div>
          </div>
          <div className="flex items-center justify-center">
            <StatsChart 
              original={result.original_raw_size} 
              compressed={result.compressed_size} 
            />
          </div>
        </div>
      )}

      {type === 'decompression' && (
        <div className="grid grid-cols-2 gap-4 mb-8">
          <StatItem 
            icon={HardDrive} 
            label="Compressed File" 
            value={result.compressed_size_formatted} 
          />
          <StatItem 
            icon={Zap} 
            label="Restored Size" 
            value={result.decompressed_size_formatted} 
            highlight={true}
          />
          <StatItem 
            icon={Clock} 
            label="Time Taken" 
            value={`${result.processing_time}s`} 
          />
        </div>
      )}

      {type === 'stego_embed' && (
        <div className="grid grid-cols-2 gap-4 mb-8">
          <StatItem 
            icon={HardDrive} 
            label="Original File" 
            value={result.original_size_formatted} 
          />
          <StatItem 
            icon={Zap} 
            label="Stego File" 
            value={result.stego_size_formatted} 
          />
          <StatItem 
            icon={Clock} 
            label="Time Taken" 
            value={`${result.processing_time}s`} 
          />
          <div className="p-4 bg-surface rounded-lg border border-border">
            <p className="text-sm text-text-secondary mb-1">Capacity Used</p>
            <p className="text-xl font-bold text-primary">
              {result.usage_percent}%
            </p>
            <p className="text-xs text-text-secondary mt-1">
              {result.message_length} / {result.capacity} bytes
            </p>
          </div>
        </div>
      )}

      {type === 'stego_extract' && (
        <div className="mb-8">
          <StatItem 
            icon={Clock} 
            label="Extraction Time" 
            value={`${result.processing_time}s`} 
            className="mb-4 w-48"
          />
          <div className="p-4 bg-surface rounded-lg border border-border">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-text-secondary">Extracted Message</p>
              <span className="text-xs px-2 py-1 bg-primary/20 text-primary rounded-full">
                {result.message_length} chars
              </span>
            </div>
            <p className="text-lg text-text-primary whitespace-pre-wrap break-words font-mono bg-background p-4 rounded border border-border">
              {result.message}
            </p>
          </div>
        </div>
      )}

      {result.download_url && (
        <div className="mt-6 pt-6 border-t border-border flex justify-end">
          <a href={result.download_url} download>
            <Button icon={Download} variant="primary">
              Download Result
            </Button>
          </a>
        </div>
      )}
    </div>
  );
};

const StatItem = ({ icon: Icon, label, value, subValue, highlight, className = '' }) => (
  <div className={`p-4 bg-surface rounded-lg border border-border ${className}`}>
    <div className="flex items-center gap-2 mb-2">
      <Icon className={`w-4 h-4 ${highlight ? 'text-primary' : 'text-text-secondary'}`} />
      <p className="text-sm text-text-secondary">{label}</p>
    </div>
    <p className={`text-xl font-bold ${highlight ? 'text-text-primary' : 'text-text-primary'}`}>
      {value}
    </p>
    {subValue && (
      <p className="text-xs text-text-secondary mt-1 truncate" title={subValue}>
        {subValue}
      </p>
    )}
  </div>
);

export default ResultCard;
