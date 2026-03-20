import { useEffect, useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { Package, Download, Star, ExternalLink, Plus, Info, ChevronRight, Activity } from 'lucide-react';
import { Link } from 'react-router-dom';

const PluginIcon = ({ plugin }) => {
    if (plugin.icon_url) {
        return <img src={plugin.icon_url} alt={plugin.name} className="plugin-icon" />;
    }
    return (
        <div className="plugin-icon" style={{ background: 'var(--accent-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent)', fontWeight: 600 }}>
            {plugin.name?.[0]?.toUpperCase() || '?'}
        </div>
    );
};

export default function Dashboard() {
    const { developerInfo, user, refreshDeveloperInfo, API_BASE, initRapnssButton } = useAuth();
    const loginContainerRef = useRef(null);
    const [allPlugins, setAllPlugins] = useState([]);
    const [loadingPlugins, setLoadingPlugins] = useState(true);

    useEffect(() => {
        if (user?.id) refreshDeveloperInfo(user.id);
    }, [user]);

    useEffect(() => {
        const fetchPublicPlugins = async () => {
            try {
                const res = await fetch(`${API_BASE}/api/plugins`);
                const data = await res.json();
                setAllPlugins(data.plugins || []);
            } catch (e) {
                console.error('Failed to fetch plugins', e);
            } finally {
                setLoadingPlugins(false);
            }
        };
        if (!user) fetchPublicPlugins();
    }, [user, API_BASE]);

    useEffect(() => {
        if (!user && loginContainerRef.current) {
            initRapnssButton('rapnss-dashboard-login').catch(console.error);
        }
    }, [user, initRapnssButton]);

    if (!user) {
        return (
            <div className="animate-fade-in" style={{ textAlign: 'center', padding: '64px 24px' }}>
                <h1 style={{ fontSize: '2.5rem', fontWeight: 300, marginBottom: '16px' }}>Horizon Play Console</h1>
                <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem', marginBottom: '32px', maxWidth: '600px', margin: '0 auto 32px' }}>
                    Publish your plugins to the Horizon Store and reach thousands of users.
                </p>
                <div id="rapnss-dashboard-login" ref={loginContainerRef} />
            </div>
        );
    }

    const plugins = developerInfo?.plugins || [];

    return (
        <div className="animate-fade-in">
            {/* Header section with Create App button */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                <div>
                    <h1 style={{ fontSize: '1.75rem', fontWeight: 400 }}>Dashboard</h1>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>An overview of your account and plugin performance</p>
                </div>
                <Link to="/upload" className="btn-primary">
                    <Plus size={18} />
                    <span>Create plugin</span>
                </Link>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
                {/* Main Content Area */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    
                    {/* Activity Summary */}
                    <div className="glass-panel">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                            <Activity size={18} color="var(--text-primary)" />
                            <h2 style={{ fontSize: '1.1rem', fontWeight: 500 }}>Account Summary</h2>
                        </div>
                        
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                            <div className="stats-card">
                                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 500 }}>PUBLISHED PLUGINS</div>
                                <div className="stats-value">{plugins.length}</div>
                            </div>
                            <div className="stats-card">
                                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 500 }}>AD CREDIT</div>
                                <div className="stats-value">${(developerInfo?.ad_balance || 0).toFixed(2)}</div>
                            </div>
                            <div className="stats-card">
                                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 500 }}>FREE RELEASES</div>
                                <div className="stats-value">{developerInfo?.free_releases_left ?? 0}</div>
                            </div>
                        </div>
                    </div>

                    {/* All Plugins List */}
                    <div className="glass-panel" style={{ padding: 0 }}>
                        <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <h2 style={{ fontSize: '1rem', fontWeight: 500 }}>Your Plugins</h2>
                            <Link to="/plugins" style={{ color: 'var(--text-primary)', fontSize: '0.85rem', fontWeight: 500, display: 'flex', alignItems: 'center' }}>
                                View all <ChevronRight size={16} />
                            </Link>
                        </div>
                        
                        {plugins.length === 0 ? (
                            <div style={{ padding: '48px 24px', textAlign: 'center' }}>
                                <Package size={48} color="var(--border)" style={{ marginBottom: '16px' }} />
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>You haven't published any plugins yet.</p>
                                <Link to="/upload" style={{ color: 'var(--text-primary)', fontWeight: 500, fontSize: '0.9rem', marginTop: '12px', display: 'inline-block' }}>
                                    Publish your first plugin
                                </Link>
                            </div>
                        ) : (
                            <div>
                                {plugins.slice(0, 5).map(plugin => (
                                    <div key={plugin.id} className="plugin-item">
                                        <PluginIcon plugin={plugin} />
                                        <div style={{ marginLeft: '16px', flex: 1 }}>
                                            <div style={{ fontWeight: 500, fontSize: '0.95rem' }}>{plugin.name}</div>
                                            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{plugin.category} • v{plugin.version}</div>
                                        </div>
                                        <div style={{ textAlign: 'right', marginRight: '24px' }}>
                                            <span className={`badge ${plugin.status === 'published' ? 'success' : 'pending'}`}>
                                                {plugin.status === 'published' ? 'Available on store' : 'Under review'}
                                            </span>
                                        </div>
                                        <ChevronRight size={18} color="var(--border)" />
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Sidebar Info Area */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    
                    {/* Task List / Getting Started */}
                    <div className="glass-panel">
                        <h2 style={{ fontSize: '1rem', fontWeight: 500, marginBottom: '16px' }}>To-do list</h2>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            {[
                                { title: 'Complete store listing', done: false, desc: 'Add screenshots and details' },
                                { title: 'Set up payments', done: true, desc: 'Add a payout method' },
                                { title: 'Verify account', done: true, desc: 'Identity verification complete' }
                            ].map((task, i) => (
                                <div key={i} style={{ display: 'flex', gap: '12px', opacity: task.done ? 0.6 : 1 }}>
                                    <div style={{ 
                                        width: 20, height: 20, borderRadius: '4px', border: `2px solid ${task.done ? 'var(--success)' : 'var(--border)'}`,
                                        background: task.done ? 'var(--success)' : 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center'
                                    }}>
                                        {task.done && <Plus size={14} color="white" style={{ transform: 'rotate(45deg)' }} />}
                                    </div>
                                    <div>
                                        <div style={{ fontSize: '0.875rem', fontWeight: 500, textDecoration: task.done ? 'line-through' : 'none' }}>{task.title}</div>
                                        {!task.done && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{task.desc}</div>}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Tips Card */}
                    <div className="glass-panel" style={{ background: 'var(--accent-light)', border: 'none' }}>
                        <div style={{ display: 'flex', gap: '12px' }}>
                            <Info size={20} color="var(--text-primary)" />
                            <div>
                                <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>Developer Tip</h3>
                                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                                    High-quality icons and clear descriptions increase installs by up to 40%.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
