import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Minimize2, Lock, Image as ImageIcon, Music, Video } from 'lucide-react';

const Sidebar = () => {
  const navGroups = [
    {
      title: 'Overview',
      items: [
        { path: '/', label: 'Dashboard', icon: LayoutDashboard }
      ]
    },
    {
      title: 'Compression',
      icon: <Minimize2 className="w-4 h-4 mr-2 text-primary" />,
      items: [
        { path: '/compression/image', label: 'Image', icon: ImageIcon },
        { path: '/compression/audio', label: 'Audio', icon: Music, disabled: true },
        { path: '/compression/video', label: 'Video', icon: Video, disabled: true },
      ]
    },
    {
      title: 'Steganography',
      icon: <Lock className="w-4 h-4 mr-2 text-secondary" />,
      items: [
        { path: '/steganography/image', label: 'Image', icon: ImageIcon },
        { path: '/steganography/audio', label: 'Audio', icon: Music, disabled: true },
        { path: '/steganography/video', label: 'Video', icon: Video, disabled: true },
      ]
    }
  ];

  return (
    <aside className="w-64 bg-surface border-r border-border h-screen flex flex-col fixed left-0 top-0">
      <div className="h-16 flex items-center px-6 border-b border-border">
        <div className="flex items-center gap-2 text-xl font-bold text-gradient">
          <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center text-primary">
            <Minimize2 className="w-5 h-5" />
          </div>
          Media Vault
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto py-6 px-4 space-y-8">
        {navGroups.map((group, idx) => (
          <div key={idx}>
            <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3 px-2 flex items-center">
              {group.icon}
              {group.title}
            </h4>
            <ul className="space-y-1">
              {group.items.map((item, itemIdx) => (
                <li key={itemIdx}>
                  {item.disabled ? (
                    <div className="flex items-center gap-3 px-3 py-2 text-text-secondary/50 rounded-lg cursor-not-allowed">
                      <item.icon className="w-5 h-5" />
                      <span className="font-medium">{item.label}</span>
                      <span className="ml-auto text-[10px] uppercase bg-surface-hover px-2 py-0.5 rounded text-text-secondary/50">Soon</span>
                    </div>
                  ) : (
                    <NavLink
                      to={item.path}
                      className={({ isActive }) => 
                        `flex items-center gap-3 px-3 py-2 rounded-lg transition-colors font-medium ${
                          isActive 
                            ? 'bg-primary/10 text-primary' 
                            : 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'
                        }`
                      }
                    >
                      <item.icon className="w-5 h-5" />
                      {item.label}
                    </NavLink>
                  )}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </aside>
  );
};

export default Sidebar;
