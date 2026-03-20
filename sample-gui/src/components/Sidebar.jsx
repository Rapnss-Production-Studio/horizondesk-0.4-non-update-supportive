import React from 'react';
import { LayoutGrid, Box, Settings, Monitor, Puzzle, LogOut, CreditCard, Users, MessageSquare } from 'lucide-react';

const Sidebar = ({ activeTab, setActiveTab }) => {
    const menuItems = [
        { id: 'home', icon: LayoutGrid, label: 'Home' },
        { id: 'teams', icon: Users, label: 'Teams' },
        { id: 'plugins', icon: Puzzle, label: 'Plugins' },
        { id: 'monitor', icon: Monitor, label: 'Monitor' },
        { id: 'settings', icon: Settings, label: 'Settings' },
        { id: 'feedback', icon: MessageSquare, label: 'Feedback' },
    ];

    return (
        <div style={{
            width: '60px',
            height: '100%',
            backgroundColor: 'var(--bg-panel)',
            borderRight: '1px solid var(--border-subtle)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            paddingTop: '20px',
            gap: '20px'
        }}>
            <div style={{ marginBottom: '20px' }}>
                {/* Logo */}
                <div style={{
                    width: '32px',
                    height: '32px',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                }} title="Horizon Desk">
                    <img src="logo.ico" alt="Horizon Desk" style={{ width: '32px', height: '32px' }} />
                </div>
            </div>

            {menuItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                    <button
                        key={item.id}
                        onClick={() => setActiveTab(item.id)}
                        title={item.label}
                        style={{
                            width: '40px',
                            height: '40px',
                            borderRadius: '8px',
                            display: 'flex',
                            justifyContent: 'center',
                            alignItems: 'center',
                            color: isActive ? 'var(--text-main)' : 'var(--text-secondary)',
                            backgroundColor: isActive ? 'var(--bg-app)' : 'transparent',
                            transition: 'all 0.2s ease'
                        }}
                    >
                        <Icon size={20} strokeWidth={1.5} />
                    </button>
                );
            })}

            <div style={{ marginTop: 'auto', marginBottom: '20px' }}>
                <button
                    title="Exit"
                    onClick={() => window.pywebview?.api?.close()}
                    style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '8px',
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        color: 'var(--text-secondary)',
                        transition: 'all 0.2s ease'
                    }}
                >
                    <LogOut size={20} strokeWidth={1.5} />
                </button>
            </div>
        </div>
    );
};

export default Sidebar;
