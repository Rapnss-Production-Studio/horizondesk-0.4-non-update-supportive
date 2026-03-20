import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Settings, User, Bell, AlertTriangle, Save, Check } from 'lucide-react';

export default function SettingsPage() {
    const { user, developerInfo, logout } = useAuth();
    const [notifications, setNotifications] = useState({
        pluginReview: true,
        weeklyDigest: false,
        securityAlerts: true,
        marketingEmails: false,
    });
    const [flash, setFlash] = useState('');

    useEffect(() => {
        const saved = localStorage.getItem('hd_notification_prefs');
        if (saved) setNotifications(JSON.parse(saved));
    }, []);

    const toggleNotif = (key) => {
        setNotifications(prev => {
            const updated = { ...prev, [key]: !prev[key] };
            localStorage.setItem('hd_notification_prefs', JSON.stringify(updated));
            return updated;
        });
    };

    const handleSave = () => {
        localStorage.setItem('hd_notification_prefs', JSON.stringify(notifications));
        setFlash('Settings saved!');
        setTimeout(() => setFlash(''), 3000);
    };

    const handleDeleteAccount = () => {
        if (confirm('Are you sure you want to delete your developer account? This cannot be undone.')) {
            logout();
        }
    };

    return (
        <div className="animate-fade-in" style={{ maxWidth: '720px' }}>
            <div style={{ marginBottom: '32px' }}>
                <h1 style={{ fontSize: '1.75rem', fontWeight: 400 }}>Settings</h1>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Manage your developer profile and preferences</p>
            </div>

            {flash && <div className="banner-success"><Check size={16} style={{ marginRight: '8px' }} />{flash}</div>}

            {/* Profile Section */}
            <div className="glass-panel" style={{ marginBottom: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                    <User size={18} color="var(--text-primary)" />
                    <h2 style={{ fontSize: '1.1rem', fontWeight: 500 }}>Developer Profile</h2>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                        <div>
                            <label className="input-label">Username</label>
                            <input className="input-field" value={user?.username || ''} disabled style={{ background: 'var(--bg)', color: 'var(--text-muted)' }} />
                        </div>
                        <div>
                            <label className="input-label">Email</label>
                            <input className="input-field" value={user?.email || ''} disabled style={{ background: 'var(--bg)', color: 'var(--text-muted)' }} />
                        </div>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                        <div>
                            <label className="input-label">Developer ID</label>
                            <input className="input-field" value={developerInfo?.id || '—'} disabled style={{ background: 'var(--bg)', color: 'var(--text-muted)', fontFamily: 'monospace', fontSize: '0.8rem' }} />
                        </div>
                        <div>
                            <label className="input-label">Account Status</label>
                            <div style={{ padding: '12px', border: '1px solid var(--border)', borderRadius: '4px', background: 'var(--bg)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--success)' }} />
                                <span style={{ color: 'var(--success)', fontWeight: 500, fontSize: '0.9rem' }}>Active Developer</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Notification Preferences */}
            <div className="glass-panel" style={{ marginBottom: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                    <Bell size={18} color="var(--accent)" />
                    <h2 style={{ fontSize: '1.1rem', fontWeight: 500 }}>Notifications</h2>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {[
                        { key: 'pluginReview', label: 'Plugin review updates', desc: 'Get notified when your plugin review status changes' },
                        { key: 'weeklyDigest', label: 'Weekly digest', desc: 'Summary of plugin performance and downloads' },
                        { key: 'securityAlerts', label: 'Security alerts', desc: 'Important security notifications about your account' },
                        { key: 'marketingEmails', label: 'Marketing emails', desc: 'Tips, news, and promotions from Horizon Desk' },
                    ].map(item => (
                        <label key={item.key} className="toggle-row" style={{ padding: '12px 0', borderBottom: '1px solid var(--border-light)' }}>
                            <div>
                                <div style={{ fontSize: '0.9rem', fontWeight: 500 }}>{item.label}</div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{item.desc}</div>
                            </div>
                            <div className={`toggle-switch ${notifications[item.key] ? 'active' : ''}`}
                                onClick={() => toggleNotif(item.key)}>
                                <div className="toggle-thumb" />
                            </div>
                        </label>
                    ))}
                </div>
            </div>

            <button className="btn-primary" onClick={handleSave} style={{ marginBottom: '32px', padding: '10px 24px' }}>
                <Save size={16} /> Save preferences
            </button>

            {/* Danger Zone */}
            <div className="danger-zone">
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                    <AlertTriangle size={18} color="var(--error)" />
                    <h2 style={{ fontSize: '1.1rem', fontWeight: 500, color: 'var(--error)' }}>Danger Zone</h2>
                </div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '16px' }}>
                    Deleting your developer account will remove all your published plugins and cannot be undone.
                </p>
                <button className="btn-danger" onClick={handleDeleteAccount}>
                    Delete developer account
                </button>
            </div>
        </div>
    );
}
