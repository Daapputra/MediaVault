import React from 'react';
import { Link } from 'react-router-dom';
import { Minimize2, Lock, Image as ImageIcon, Music, Video, ArrowRight, Zap, Shield, FileOutput } from 'lucide-react';

const Dashboard = () => {
  const features = [
    {
      title: 'Lossless Compression',
      description: 'Compress your media files without losing a single byte of original data using custom Huffman & RLE algorithms.',
      icon: Zap,
      color: 'text-warning',
      bg: 'bg-warning/10'
    },
    {
      title: 'Secure Steganography',
      description: 'Hide secret messages inside your media files using LSB (Least Significant Bit) manipulation techniques.',
      icon: Shield,
      color: 'text-success',
      bg: 'bg-success/10'
    },
    {
      title: 'Multiple Formats',
      description: 'Support for Images (PNG, BMP), Audio (WAV), and Video (AVI, MP4) processing natively.',
      icon: FileOutput,
      color: 'text-primary',
      bg: 'bg-primary/10'
    }
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-12 animate-fade-in pb-12">
      {/* Hero Section */}
      <section className="text-center py-12">
        <div className="inline-flex items-center justify-center p-3 bg-primary/10 text-primary rounded-2xl mb-6">
          <Minimize2 className="w-12 h-12" />
        </div>
        <h1 className="text-4xl md:text-5xl font-bold text-text-primary mb-6">
          Advanced Media <span className="text-gradient">Processing Hub</span>
        </h1>
        <p className="text-lg text-text-secondary max-w-2xl mx-auto mb-10">
          A powerful suite for lossless media compression and secure steganography, built with modern algorithms from scratch.
        </p>
        
        <div className="flex items-center justify-center gap-4">
          <Link to="/compression/image" className="px-6 py-3 bg-primary hover:bg-primary-hover text-white rounded-lg font-medium transition-colors shadow-lg shadow-primary/20 flex items-center gap-2">
            Try Compression <ArrowRight className="w-4 h-4" />
          </Link>
          <Link to="/steganography/image" className="px-6 py-3 bg-surface hover:bg-surface-hover border border-border text-text-primary rounded-lg font-medium transition-colors flex items-center gap-2">
            Try Steganography <Lock className="w-4 h-4" />
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {features.map((feature, idx) => (
          <div key={idx} className="glass-panel p-6 hover:-translate-y-1 transition-transform duration-300">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${feature.bg} ${feature.color}`}>
              <feature.icon className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-semibold text-text-primary mb-2">{feature.title}</h3>
            <p className="text-text-secondary leading-relaxed">
              {feature.description}
            </p>
          </div>
        ))}
      </section>

      {/* Modules */}
      <section className="space-y-6">
        <h2 className="text-2xl font-bold text-text-primary">Available Modules</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Compression Card */}
          <div className="glass-panel p-6 border-l-4 border-l-primary relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
              <Minimize2 className="w-32 h-32 text-primary" />
            </div>
            
            <h3 className="text-2xl font-bold text-text-primary mb-2">Compression</h3>
            <p className="text-text-secondary mb-6">Reduce file sizes efficiently while maintaining 100% original quality.</p>
            
            <div className="flex gap-3">
              <Link to="/compression/image" className="flex items-center gap-2 px-4 py-2 bg-surface border border-border rounded-lg hover:border-primary hover:text-primary transition-colors text-sm font-medium text-text-secondary">
                <ImageIcon className="w-4 h-4" /> Image
              </Link>
              <button disabled className="flex items-center gap-2 px-4 py-2 bg-background border border-border rounded-lg opacity-50 cursor-not-allowed text-sm font-medium text-text-secondary">
                <Music className="w-4 h-4" /> Audio
              </button>
              <button disabled className="flex items-center gap-2 px-4 py-2 bg-background border border-border rounded-lg opacity-50 cursor-not-allowed text-sm font-medium text-text-secondary">
                <Video className="w-4 h-4" /> Video
              </button>
            </div>
          </div>

          {/* Steganography Card */}
          <div className="glass-panel p-6 border-l-4 border-l-secondary relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
              <Lock className="w-32 h-32 text-secondary" />
            </div>
            
            <h3 className="text-2xl font-bold text-text-primary mb-2">Steganography</h3>
            <p className="text-text-secondary mb-6">Hide your secret messages invisibly inside standard media files.</p>
            
            <div className="flex gap-3">
              <Link to="/steganography/image" className="flex items-center gap-2 px-4 py-2 bg-surface border border-border rounded-lg hover:border-secondary hover:text-secondary transition-colors text-sm font-medium text-text-secondary">
                <ImageIcon className="w-4 h-4" /> Image
              </Link>
              <button disabled className="flex items-center gap-2 px-4 py-2 bg-background border border-border rounded-lg opacity-50 cursor-not-allowed text-sm font-medium text-text-secondary">
                <Music className="w-4 h-4" /> Audio
              </button>
              <button disabled className="flex items-center gap-2 px-4 py-2 bg-background border border-border rounded-lg opacity-50 cursor-not-allowed text-sm font-medium text-text-secondary">
                <Video className="w-4 h-4" /> Video
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
