
import React, { useState, useEffect } from 'react';
import { User, Mail, Lock, ShieldCheck, ArrowRight } from 'lucide-react';

const Login = ({ onLogin }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const API_BASE = 'https://horizon-online.api-rapnss.workers.dev'; // Worker URL (fallback for browser testing)

    // Core exchange function - routes through Python API to avoid file:// CORS issues
    const doExchange = async (code) => {
        setLoading(true);
        setError('');
        try {
            let result;
            if (window.pywebview?.api) {
                // PREFERRED PATH: Use Python backend directly (no CORS issues from file://)
                result = await window.pywebview.api.exchange_oauth_code(code);
            } else {
                // FALLBACK: For browser testing only (requires wrangler dev running)
                const res = await fetch(`${API_BASE}/api/auth/oauth-exchange`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code, redirectUri: 'http://127.0.0.1:5173/auth/callback' })
                });
                result = await res.json();
            }

            if (result.success) {
                onLogin(result.user);
            } else {
                const details = result.details ? ` — ${JSON.stringify(result.details)}` : '';
                setError((result.error || "OAuth login failed") + details);
            }
        } catch (err) {
            setError(err.message || String(err));
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        // Load Rapnss SDK
        const script = document.createElement('script');
        script.src = 'https://rapnss.in/api/auth/sdk.js';
        script.async = true;

        script.onload = () => {
            if (window.RapnssAuth) {
                window.RapnssAuth.init({
                    clientId: import.meta.env.VITE_RAPNSS_CLIENT_ID || 'client_e759717477b44e89b3aa983071baceb7',
                    redirectUri: 'http://127.0.0.1:5173/auth/callback',
                    containerId: 'rapnss-login',
                    onSuccess: async function (data) {
                        await doExchange(data.code);
                    },
                    onError: function (err) {
                        console.error('Rapnss Auth Error:', err);
                        setError("Rapnss Login Error: " + err);
                    }
                });
            }
        };
        document.body.appendChild(script);

        // Called directly by the local Python OAuth server after code injection
        window.handleOAuthCallback = async (code) => {
            console.log("Received OAuth code from local Python server:", code);
            await doExchange(code);
        };

        return () => {
            try { document.body.removeChild(script); } catch (e) { }
            delete window.handleOAuthCallback;
        };
    }, [onLogin]);

    return (
        <div style={{
            height: '100%', display: 'flex', flexDirection: 'column',
            justifyContent: 'center', alignItems: 'center', backgroundColor: 'var(--bg-app)'
        }}>
            <div style={{ marginBottom: '30px', textAlign: 'center' }}>
                <img src="logo.ico" alt="Horizon Desk" style={{ width: '64px', height: '64px', marginBottom: '15px' }} />
                <h1 style={{ margin: 0 }}>Horizon Desk</h1>
                <p style={{ color: 'var(--text-secondary)' }}>Next-Gen Agentic Workspace</p>
            </div>

            <div className="card" style={{ width: '400px', padding: '40px', display: 'flex', flexDirection: 'column', gap: '20px', alignItems: 'center' }}>
                <h2 style={{ marginTop: 0, textAlign: 'center' }}>Access Workspace</h2>

                {error && <div style={{ color: 'var(--red)', textAlign: 'center', fontSize: '0.9em', width: '100%' }}>{error}</div>}
                {loading && <div style={{ color: 'var(--text-secondary)', textAlign: 'center', fontSize: '0.9em' }}>Signing you in...</div>}

                <div id="rapnss-login" style={{ width: '100%', display: 'flex', justifyContent: 'center', marginTop: '10px' }}></div>

                <p style={{ fontSize: '0.85em', color: 'var(--text-secondary)', textAlign: 'center', marginTop: '20px' }}>
                    Authentication is securely powered by Rapnss OAuth.
                </p>
            </div>
        </div>
    );
};

export default Login;
