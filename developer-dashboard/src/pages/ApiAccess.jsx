import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Code, Copy, Check, Terminal, Key, BarChart3 } from 'lucide-react';

export default function ApiAccess() {
    const { developerInfo, user } = useAuth();
    const [copied, setCopied] = useState(false);

    const apiKey = developerInfo?.id ? `hd_${developerInfo.id.replace(/-/g, '').slice(0, 32)}` : '—';
    const plugins = developerInfo?.plugins || [];

    const copyKey = () => {
        navigator.clipboard.writeText(apiKey);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="animate-fade-in">
            <div style={{ marginBottom: '32px' }}>
                <h1 style={{ fontSize: '1.75rem', fontWeight: 400 }}>API Access</h1>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Your developer API key and CLI integration guide</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
                {/* API Key */}
                <div className="glass-panel">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                        <Key size={18} color="var(--text-primary)" />
                        <h2 style={{ fontSize: '1.1rem', fontWeight: 500 }}>Developer API Key</h2>
                    </div>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '16px' }}>
                        Use this key to authenticate API requests and CLI commands.
                    </p>
                    <div style={{
                        display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--bg)',
                        padding: '12px 16px', borderRadius: '6px', border: '1px solid var(--border)', fontFamily: 'monospace', fontSize: '0.85rem'
                    }}>
                        <code style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>{apiKey}</code>
                        <button className="btn-icon" onClick={copyKey} title="Copy">
                            {copied ? <Check size={16} color="var(--success)" /> : <Copy size={16} />}
                        </button>
                    </div>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '8px' }}>
                        Keep this key secret. Do not share it publicly.
                    </p>
                </div>

                {/* Usage Stats */}
                <div className="glass-panel">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                        <BarChart3 size={18} color="var(--success)" />
                        <h2 style={{ fontSize: '1.1rem', fontWeight: 500 }}>Usage Overview</h2>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                        <div className="stats-card">
                            <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 500 }}>TOTAL PLUGINS</div>
                            <div className="stats-value" style={{ fontSize: '1.75rem' }}>{plugins.length}</div>
                        </div>
                        <div className="stats-card">
                            <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 500 }}>FREE RELEASES</div>
                            <div className="stats-value" style={{ fontSize: '1.75rem' }}>{developerInfo?.free_releases_left ?? 0}</div>
                        </div>
                        <div className="stats-card">
                            <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 500 }}>AD BALANCE</div>
                            <div className="stats-value" style={{ fontSize: '1.75rem' }}>${(developerInfo?.ad_balance || 0).toFixed(2)}</div>
                        </div>
                        <div className="stats-card">
                            <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 500 }}>ACCOUNT STATUS</div>
                            <div className="stats-value" style={{ fontSize: '1.75rem', color: 'var(--success)' }}>Active</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* CLI Guide */}
            <div className="glass-panel">
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                    <Terminal size={18} color="var(--accent)" />
                    <h2 style={{ fontSize: '1.1rem', fontWeight: 500 }}>CLI Quick Start</h2>
                </div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '20px' }}>
                    Use the Horizon Desk CLI to publish plugins directly from your terminal.
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <div className="code-block">
                        <div className="code-label">1. Install the SDK</div>
                        <pre><code>pip install horizondesk</code></pre>
                    </div>
                    <div className="code-block">
                        <div className="code-label">2. Login with your Rapnss account</div>
                        <pre><code>horizondesk login</code></pre>
                    </div>
                    <div className="code-block">
                        <div className="code-label">3. Create a new plugin</div>
                        <pre><code>horizondesk init MyPlugin{'\n'}cd MyPlugin</code></pre>
                    </div>
                    <div className="code-block">
                        <div className="code-label">4. Test locally</div>
                        <pre><code>horizondesk test --prompt "List your tools"</code></pre>
                    </div>
                    <div className="code-block">
                        <div className="code-label">5. Publish to the Horizon Store</div>
                        <pre><code>horizondesk publish</code></pre>
                    </div>
                    <div className="code-block">
                        <div className="code-label">6. Check your published plugins</div>
                        <pre><code>horizondesk status</code></pre>
                    </div>
                </div>
            </div>
        </div>
    );
}
