import React, { useState, useEffect } from 'react';
import { Globe, ArrowRight, Languages, Cpu } from 'lucide-react';

const Onboarding = ({ onComplete }) => {
    const [language, setLanguage] = useState('English (US)');
    const [loading, setLoading] = useState(false);

    const handleComplete = async () => {
        setLoading(true);
        
        // Auto-fetch timezone and country
        let timezone = 'UTC';
        let country = 'Unknown';
        
        try {
            const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
            const offset = new Date().getTimezoneOffset();
            const absOffset = Math.abs(offset);
            const hours = Math.floor(absOffset / 60);
            const minutes = absOffset % 60;
            const sign = offset <= 0 ? '+' : '-';
            const formattedOffset = `(UTC${sign}${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')})`;
            timezone = `${tz} ${formattedOffset}`;
            
            // Basic country detection based on timezone if possible, or leave as Unknown/Detect later
            if (tz.includes('India') || tz.includes('Calcutta')) country = 'India';
            else if (tz.includes('New_York') || tz.includes('Los_Angeles')) country = 'United States';
            else if (tz.includes('London')) country = 'United Kingdom';
            else country = tz.split('/')[0] || 'Global';
        } catch (e) {
            console.error('Fetch error:', e);
        }

        // Save to local storage
        localStorage.setItem('horizon_onboarding_done', 'true');
        localStorage.setItem('horizon_initial_config', JSON.stringify({
            language, country, timezone
        }));
        
        // Persist language specifically for application use
        localStorage.setItem('horizon_language', language);

        // Notify backend
        if (window.pywebview?.api) {
            try {
                await window.pywebview.api.save_parameters({ language, country, timezone });
            } catch (e) {
                console.error('API Error:', e);
            }
        }
        
        setLoading(false);
        onComplete();
    };

    return (
        <div style={{
            height: '100%', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center',
            backgroundColor: 'var(--bg-app)', // Matches Home.jsx
            color: 'var(--text-main)',
            fontFamily: 'var(--font-sans)'
        }}>
            <div style={{
                width: '440px', padding: '48px', display: 'flex', flexDirection: 'column', gap: '32px',
                backgroundColor: 'var(--bg-panel)', 
                borderRadius: '24px',
                boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                border: '1px solid var(--border-subtle)',
                textAlign: 'center'
            }}>
                {/* Logo Area */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
                    <div style={{
                        width: '64px', height: '64px', borderRadius: '16px', 
                        backgroundColor: 'var(--accent)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        boxShadow: '0 10px 15px -3px rgba(16, 163, 127, 0.3)'
                    }}>
                        <Cpu size={36} color="white" />
                    </div>
                    <div>
                        <h1 style={{ fontSize: '28px', fontWeight: 800, letterSpacing: '-0.025em', color: 'var(--text-main)' }}>Horizon Desk</h1>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '15px', marginTop: '4px' }}>Welcome to your workspace.</p>
                    </div>
                </div>

                <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <label style={{ 
                        display: 'flex', alignItems: 'center', gap: '8px', 
                        fontSize: '14px', fontWeight: 600, color: 'var(--text-main)' 
                    }}>
                        <Languages size={16} color="var(--accent)" /> Select your language
                    </label>
                    <select 
                        value={language} 
                        onChange={e => setLanguage(e.target.value)} 
                        style={{
                            width: '100%', padding: '14px', borderRadius: '12px', 
                            border: '2px solid var(--border-subtle)',
                            backgroundColor: 'white', color: 'var(--text-main)',
                            fontSize: '15px', outline: 'none', cursor: 'pointer',
                            appearance: 'none',
                            backgroundImage: `url("data:image/svg+xml;charset=UTF-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpolyline%20points%3D%226%209%2012%2015%2018%209%22%3E%3C%2Fpolyline%3E%3C%2Fsvg%3E")`,
                            backgroundRepeat: 'no-repeat',
                            backgroundPosition: 'right 12px center',
                            backgroundSize: '16px'
                        }}
                    >
                        <option>English (US)</option>
                        <option>English (UK)</option>
                        <option>Spanish (ES)</option>
                        <option>French (FR)</option>
                        <option>German (DE)</option>
                        <option>Hindi (IN)</option>
                        <option>Chinese (Simplified)</option>
                        <option>Japanese (JP)</option>
                    </select>
                    <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                        This will be used for your interface and AI interactions.
                    </p>
                </div>

                <button 
                    onClick={handleComplete} 
                    disabled={loading}
                    style={{
                        padding: '16px', borderRadius: '14px', border: 'none', 
                        backgroundColor: 'var(--accent)',
                        color: 'white', fontWeight: 700, fontSize: '16px', 
                        cursor: loading ? 'default' : 'pointer', 
                        display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px', 
                        transition: 'all 0.2s',
                        opacity: loading ? 0.7 : 1,
                        boxShadow: '0 4px 14px 0 rgba(16, 163, 127, 0.39)'
                    }}
                >
                    {loading ? 'Setting up...' : 'Complete Setup'} 
                    {!loading && <ArrowRight size={20} />}
                </button>
            </div>
        </div>
    );
};

export default Onboarding;
