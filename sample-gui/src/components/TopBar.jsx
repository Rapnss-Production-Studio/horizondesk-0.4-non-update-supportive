import React, { useState } from 'react';
import { Minus, Square, X, Search, ChevronRight } from 'lucide-react';

const TopBar = ({ title, setActiveTab }) => {
    const [isHovered, setIsHovered] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');

    const handleSearch = (e) => {
        const query = e.target.value.toLowerCase();
        setSearchQuery(query);

        if (!setActiveTab) return;

        // Global routing based on keywords
        if (query.includes('setting') || query.includes('config') || query.includes('preference')) {
            setActiveTab('settings');
        } else if (query.includes('plugin') || query.includes('store') || query.includes('extension')) {
            setActiveTab('plugins');
        } else if (query.includes('team') || query.includes('member') || query.includes('group')) {
            setActiveTab('teams');
        } else if (query.includes('monitor') || query.includes('system') || query.includes('usage') || query.includes('cpu')) {
            setActiveTab('monitor');
        } else if (query.includes('feedback') || query.includes('bug') || query.includes('report') || query.includes('help')) {
            setActiveTab('feedback');
        } else if (query.includes('home') || query.includes('dashboard')) {
            setActiveTab('home');
        }
    };

    const handleMinimize = () => {
        if (window.pywebview?.api) {
            window.pywebview.api.minimize();
        }
    };

    const handleClose = () => {
        if (window.pywebview?.api) {
            window.pywebview.api.close();
        }
    };

    return (
        <div style={{
            height: '40px',
            backgroundColor: 'var(--bg-panel)',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 16px',
            userSelect: 'none'
        }}>
            {/* Logo and Breadcrumb / Title */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <img src="logo.ico" alt="Logo" style={{ width: '22px', height: '22px' }} onError={(e) => e.target.style.display = 'none'} />
                <div style={{
                    fontSize: '13px',
                    fontWeight: 500,
                    color: 'var(--text-secondary)',
                    fontFamily: 'var(--font-sans)'
                }}>
                    Horizon Desk <span style={{ margin: '0 6px' }}>/</span> <span style={{ color: 'var(--text-main)' }}>{title}</span>
                </div>
            </div>

            {/* Search Bar Placeholder */}
            <div style={{
                flex: 1,
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center'
            }}>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    backgroundColor: 'var(--bg-app)',
                    padding: '4px 12px',
                    borderRadius: '6px',
                    border: '1px solid var(--border-subtle)',
                    width: '300px',
                    height: '28px'
                }}>
                    <Search size={14} color="var(--text-secondary)" />
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={handleSearch}
                        placeholder="Search tasks, plugins, or files..."
                        style={{
                            border: 'none',
                            background: 'transparent',
                            outline: 'none',
                            fontSize: '12px',
                            width: '100%',
                            color: 'var(--text-main)'
                        }}
                    />
                </div>
            </div>

            {/* Window Controls & Logs */}
            <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                {/* Log Toggle (Claude style) */}
                <button 
                    onClick={() => window.dispatchEvent(new CustomEvent('toggle-logs'))}
                    style={{
                        padding: '6px', borderRadius: '4px', color: 'var(--text-secondary)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        transition: 'all 0.2s'
                    }}
                    className="titlebar-btn"
                >
                    <ChevronRight size={16} />
                </button>

                <div style={{ width: '1px', height: '16px', background: 'var(--border-subtle)', margin: '0 4px' }} />

                <button onClick={handleMinimize} className="titlebar-btn" style={{ padding: '8px' }}>
                    <Minus size={14} />
                </button>
                <button className="titlebar-btn" style={{ padding: '8px' }}>
                    <Square size={12} />
                </button>
                <button onClick={handleClose} className="titlebar-btn-close" style={{ padding: '8px' }}>
                    <X size={14} />
                </button>
            </div>

            <style>{`
                .titlebar-btn {
                    border-radius: 4px;
                    transition: all 0.2s;
                    color: var(--text-secondary);
                }
                .titlebar-btn:hover {
                    background: var(--bg-selected);
                    color: var(--accent);
                }
                .titlebar-btn-close {
                    border-radius: 4px;
                    transition: all 0.2s;
                    color: var(--text-secondary);
                }
                .titlebar-btn-close:hover {
                    background: #f43f5e;
                    color: white;
                }
            `}</style>
        </div>
    );
};

export default TopBar;
