import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * OAuthCallback — receives the code from Rapnss OAuth popup redirect.
 * The Rapnss SDK may open a popup that lands on this page; we detect the code,
 * exchange it, then navigate home.
 */
export default function OAuthCallback() {
    const location = useLocation();
    const navigate = useNavigate();
    const { handleOAuthCallback } = useAuth();

    useEffect(() => {
        const run = async () => {
            const params = new URLSearchParams(location.search);
            const code = params.get('code');

            if (code) {
                try {
                    await handleOAuthCallback(code);
                    navigate('/', { replace: true });
                } catch (e) {
                    console.error('[OAuthCallback] Exchange failed:', e);
                    navigate('/onboarding', { replace: true });
                }
            } else {
                // No code — just go home
                navigate('/', { replace: true });
            }
        };
        run();
    }, [location, handleOAuthCallback, navigate]);

    return (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
            <div className="glass-panel" style={{ textAlign: 'center', padding: '48px 32px' }}>
                <div style={{ fontSize: '2rem', marginBottom: '16px' }}>⏳</div>
                <h2 className="page-title" style={{ fontSize: '1.5rem', marginBottom: '16px' }}>Signing you in...</h2>
                <p className="page-subtitle">Verifying your Rapnss account.</p>
            </div>
        </div>
    );
}
