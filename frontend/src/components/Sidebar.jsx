import React, { useState } from 'react';
import '../styles/sidebar.css';

export default function Sidebar({ currentPage, onNavigate, isDataLoaded }) {
  const [isOpen, setIsOpen] = useState(false);

  const menuItems = [
    { id: 'home', label: 'Home', icon: '🏠' },
    { id: 'analysis', label: 'Analysis', icon: '📊', locked: !isDataLoaded },
    { id: 'report', label: 'Executive Summary / Report', icon: '👑', locked: !isDataLoaded },
    { id: 'scenedetail', label: 'Detailed Scene View', icon: '🎬', locked: !isDataLoaded },
  ];

  const handleNavClick = (pageId) => {
    const item = menuItems.find(m => m.id === pageId);
    if (item && item.locked) return;
    onNavigate(pageId);
  };

  return (
    <div 
      className={`sidebar ${isOpen ? 'open' : 'closed'}`}
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
    >
      <div className="sidebar-header">
        <h1 className="app-title">CineSafe</h1>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map(item => (
          <div key={item.id} className="nav-item-wrapper">
            <button
              className={`nav-item ${currentPage === item.id ? 'active' : ''} ${item.locked ? 'locked' : ''}`}
              onClick={() => handleNavClick(item.id)}
              disabled={item.locked}
              title={item.locked ? 'Available after analysis completes' : item.label}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
              {item.locked && <span className="lock-icon">🔒</span>}
            </button>
          </div>
        ))}
      </nav>
    </div>
  );
}
