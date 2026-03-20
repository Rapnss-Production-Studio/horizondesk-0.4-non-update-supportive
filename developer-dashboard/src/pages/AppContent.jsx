import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { BarChart3, Shield, Lock, ChevronDown, Save, Check } from 'lucide-react';

const RATINGS = ['Everyone', 'Teen', 'Mature'];
const DATA_OPTIONS = [
    { key: 'collectsLocation', label: 'Location data' },
    { key: 'collectsFiles', label: 'File system access' },
    { key: 'collectsPersonal', label: 'Personal information' },
    { key: 'sendsAnalytics', label: 'Usage analytics' },
    { key: 'usesNetwork', label: 'Network access' },
];

export default function AppContent() {
    const { developerInfo, user, refreshDeveloperInfo } = useAuth();
    const [selectedId, setSelectedId] = useState('');
    const [contentRating, setContentRating] = useState('Everyone');
    const [dataSafety, setDataSafety] = useState({});
    const [privacyUrl, setPrivacyUrl] = useState('');
    const [termsUrl, setTermsUrl] = useState('');
    const [flash, setFlash] = useState('');

    useEffect(() => { if (user?.id) refreshDeveloperInfo(user.id); }, [user]);

    const plugins = developerInfo?.plugins || [];

    useEffect(() => {
        if (selectedId) {
            const saved = localStorage.getItem(`hd_content_${selectedId}`);
            if (saved) {
                const data = JSON.parse(saved);
                setContentRating(data.contentRating || 'Everyone');
                setDataSafety(data.dataSafety || {});
                setPrivacyUrl(data.privacyUrl || '');
                setTermsUrl(data.termsUrl || '');
            } else {
                setContentRating('Everyone');
                setDataSafety({});
                setPrivacyUrl('');
                setTermsUrl('');
            }
        }
    }, [selectedId]);

    const handleSave = () => {
        if (!selectedId) return;
        localStorage.setItem(`hd_content_${selectedId}`, JSON.stringify({ contentRating, dataSafety, privacyUrl, termsUrl }));
        setFlash('Content settings saved!');
        setTimeout(() => setFlash(''), 3000);
    };

    return (
        <div className="animate-fade-in">
            <div style={{ marginBottom: '32px' }}>
                <h1 style={{ fontSize: '1.75rem', fontWeight: 400 }}>App Content</h1>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Content rating, data safety, and compliance for your plugins</p>
            </div>

            {flash && <div className="banner-success"><Check size={16} style={{ marginRight: '8px' }} />{flash}</div>}

            {/* Plugin Selector */}
            <div className="glass-panel" style={{ marginBottom: '24px' }}>
                <label className="input-label">Select plugin</label>
                <div style={{ position: 'relative' }}>
                    <select className="input-field" value={selectedId} onChange={e => setSelectedId(e.target.value)} style={{ appearance: 'none', paddingRight: '32px' }}>
                        <option value="">— Choose a plugin —</option>
                        {plugins.map(p => <option key={p.id} value={p.id}>{p.name} (v{p.version})</option>)}
                    </select>
                    <ChevronDown size={16} style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', color: 'var(--text-muted)' }} />
                </div>
            </div>

            {!selectedId ? (
                <div className="glass-panel" style={{ textAlign: 'center', padding: '64px 24px' }}>
                    <BarChart3 size={48} color="var(--border)" style={{ marginBottom: '16px' }} />
                    <p style={{ color: 'var(--text-muted)' }}>Select a plugin above to configure its content settings.</p>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    {/* Content Rating */}
                    <div className="glass-panel">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                            <Shield size={18} color="var(--text-primary)" />
                            <h2 style={{ fontSize: '1.1rem', fontWeight: 500 }}>Content Rating</h2>
                        </div>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '16px' }}>
                            Choose a content rating based on the nature of your plugin's functionality.
                        </p>
                        <div style={{ display: 'flex', gap: '12px' }}>
                            {RATINGS.map(r => (
                                <button key={r} onClick={() => setContentRating(r)}
                                    className={contentRating === r ? 'btn-primary' : 'btn-secondary'}
                                    style={{ flex: 1, padding: '12px', fontSize: '0.9rem' }}>
                                    {r}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Data Safety */}
                    <div className="glass-panel">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                            <Lock size={18} color="var(--success)" />
                            <h2 style={{ fontSize: '1.1rem', fontWeight: 500 }}>Data Safety</h2>
                        </div>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '16px' }}>
                            Declare what data your plugin accesses. This is displayed to users before installation.
                        </p>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            {DATA_OPTIONS.map(opt => (
                                <label key={opt.key} className="toggle-row">
                                    <span style={{ fontSize: '0.9rem' }}>{opt.label}</span>
                                    <div className={`toggle-switch ${dataSafety[opt.key] ? 'active' : ''}`}
                                        onClick={() => setDataSafety({ ...dataSafety, [opt.key]: !dataSafety[opt.key] })}>
                                        <div className="toggle-thumb" />
                                    </div>
                                </label>
                            ))}
                        </div>
                    </div>

                    {/* Privacy & Terms */}
                    <div className="glass-panel">
                        <h2 style={{ fontSize: '1.1rem', fontWeight: 500, marginBottom: '20px' }}>Compliance Links</h2>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            <div>
                                <label className="input-label">Privacy Policy URL</label>
                                <input className="input-field" type="url" value={privacyUrl}
                                    onChange={e => setPrivacyUrl(e.target.value)} placeholder="https://yoursite.com/privacy" />
                            </div>
                            <div>
                                <label className="input-label">Terms of Service URL</label>
                                <input className="input-field" type="url" value={termsUrl}
                                    onChange={e => setTermsUrl(e.target.value)} placeholder="https://yoursite.com/terms" />
                            </div>
                        </div>
                    </div>

                    <button className="btn-primary" onClick={handleSave} style={{ alignSelf: 'flex-start', padding: '10px 24px' }}>
                        <Save size={16} /> Save content settings
                    </button>
                </div>
            )}
        </div>
    );
}
