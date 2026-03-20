import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, Target, Lock, ChevronRight } from 'lucide-react';

export default function Onboarding() {
    const { user, initRapnssButton, acceptTerms } = useAuth();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const sdkContainerRef = useRef(null);

    // Mount the Rapnss SDK login button once we know the user isn't logged in yet
    useEffect(() => {
        if (!user && sdkContainerRef.current) {
            initRapnssButton('rapnss-login-btn').catch((e) => {
                setError('Could not load login button. Please refresh the page.');
                console.error(e);
            });
        }
    }, [user, initRapnssButton]);

    const handleAgree = async () => {
        setLoading(true);
        setError('');
        try {
            await acceptTerms();
        } catch (e) {
            setError('Failed to accept terms. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="animate-fade-in" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
            <div className="glass-panel" style={{ maxWidth: '640px', width: '100%', padding: '48px' }}>
                <div style={{ textAlign: 'center', marginBottom: '40px' }}>
                    <div style={{ 
                        width: 64, height: 64, borderRadius: '50%', background: 'var(--accent-light)', 
                        display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px'
                    }}>
                        <ShieldCheck size={32} color="var(--accent)" />
                    </div>
                    <h1 style={{ fontSize: '1.75rem', fontWeight: 400, marginBottom: '12px' }}>Welcome to the Developer Program</h1>
                    <p style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>Before you start publishing, please review our developer policies.</p>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', marginBottom: '40px' }}>
                    <div style={{ display: 'flex', gap: '20px' }}>
                        <div style={{ 
                            width: 40, height: 40, borderRadius: '8px', background: '#e6f4ea', 
                            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 
                        }}>
                            <Lock size={20} color="var(--success)" />
                        </div>
                        <div>
                            <h4 style={{ fontSize: '1rem', fontWeight: 500, marginBottom: '6px' }}>1. Strict Data Protection</h4>
                            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.5 }}>
                                Plugins must never exfiltrate user API keys, files, or personal data. All processing must happen locally or via authorized API endpoints.
                            </p>
                        </div>
                    </div>

                    <div style={{ display: 'flex', gap: '20px' }}>
                        <div style={{ 
                            width: 40, height: 40, borderRadius: '8px', background: '#fef7e0', 
                            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 
                        }}>
                            <Target size={20} color="#b06000" />
                        </div>
                        <div>
                            <h4 style={{ fontSize: '1rem', fontWeight: 500, marginBottom: '6px' }}>2. Review & Moderation</h4>
                            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.5 }}>
                                All uploaded plugins are scanned. Submitting malicious code results in an immediate ban from the Rapnss platform.
                            </p>
                        </div>
                    </div>
                </div>

                <div style={{ background: 'var(--accent-light)', padding: '20px', borderRadius: '8px', marginBottom: '32px', border: '1px solid var(--accent-light)' }}>
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                        <span style={{ fontSize: '1.1rem' }}>🎉</span>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text)', lineHeight: 1.4 }}>
                            <strong>Welcome Bonus:</strong> Join today and get <strong>1 free plugin release</strong> and <strong>$10.00 in Ad Credits</strong> to promote your work.
                        </div>
                    </div>
                </div>

                {error && <div className="banner-error" style={{ marginBottom: '24px' }}>{error}</div>}

                {!user ? (
                    <div style={{ textAlign: 'center' }}>
                        <div id="rapnss-login-btn" ref={sdkContainerRef} style={{ marginBottom: '20px' }} />
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            A verified Rapnss account is required to participate.
                        </p>
                    </div>
                ) : (
                    <button
                        onClick={handleAgree}
                        disabled={loading}
                        className="btn-primary"
                        style={{ width: '100%', padding: '12px', fontSize: '1rem' }}
                    >
                        {loading ? 'Processing...' : 'Accept & Continue'}
                        {!loading && <ChevronRight size={18} style={{ marginLeft: '8px' }} />}
                    </button>
                )}
            </div>
        </div>
    );
}
