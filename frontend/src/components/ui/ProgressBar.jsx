import React from 'react';

const ProgressBar = ({ progress = 0, label = "Processing...", isIndeterminate = false }) => {
  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-text-primary">{label}</span>
        {!isIndeterminate && (
          <span className="text-sm font-medium text-text-secondary">{Math.round(progress)}%</span>
        )}
      </div>
      
      <div className="h-2.5 bg-surface-hover rounded-full overflow-hidden relative">
        {isIndeterminate ? (
          <div className="absolute top-0 bottom-0 left-0 w-1/3 bg-primary rounded-full animate-[progress_1.5s_ease-in-out_infinite]" />
        ) : (
          <div 
            className="h-full bg-gradient-to-r from-primary to-secondary rounded-full transition-all duration-300 ease-out"
            style={{ width: `${Math.max(0, Math.min(100, progress))}%` }}
          />
        )}
      </div>
      
      <style>{`
        @keyframes progress {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(300%); }
        }
      `}</style>
    </div>
  );
};

export default ProgressBar;
