import React from 'react';
import { useLocation } from 'react-router-dom';

const Header = () => {
  const location = useLocation();
  
  // Format the path into a readable title
  const getTitle = () => {
    const path = location.pathname;
    if (path === '/') return 'Dashboard';
    
    // e.g. /compression/image -> Compression / Image
    const parts = path.split('/').filter(Boolean);
    return parts.map(part => part.charAt(0).toUpperCase() + part.slice(1)).join(' / ');
  };

  return (
    <header className="h-16 bg-background/80 backdrop-blur-md border-b border-border flex items-center px-8 sticky top-0 z-10">
      <h1 className="text-xl font-semibold text-text-primary">
        {getTitle()}
      </h1>
      
      <div className="ml-auto flex items-center gap-4">
        <div className="text-sm text-text-secondary bg-surface px-3 py-1.5 rounded-full border border-border">
          Status: <span className="text-success font-medium flex items-center inline-flex gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-success"></span> API Connected</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
