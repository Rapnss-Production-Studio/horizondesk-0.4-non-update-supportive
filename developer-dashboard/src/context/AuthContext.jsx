import { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

// Rapnss OAuth Config
const CLIENT_ID = 'client_8d8f818e2b314b4c9625c90f5d98a70f';
const API_BASE = 'https://horizon-online.api-rapnss.workers.dev';

// Dynamically load the Rapnss SDK script once
let sdkLoaded = false;
function loadRapnssSDK() {
    return new Promise((resolve, reject) => {
        if (sdkLoaded || window.RapnssAuth) {
            sdkLoaded = true;
            return resolve();
        }
        const script = document.createElement('script');
        script.src = 'https://rapnss.in/api/auth/sdk.js';
        script.onload = () => {
            sdkLoaded = true;
            resolve();
        };
        script.onerror = () => reject(new Error('Failed to load Rapnss SDK'));
        document.head.appendChild(script);
    });
}

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [developerInfo, setDeveloperInfo] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const savedUser = localStorage.getItem('horizon_dev_user');
        const savedInfo = localStorage.getItem('horizon_dev_info');
        if (savedUser) setUser(JSON.parse(savedUser));
        if (savedInfo) setDeveloperInfo(JSON.parse(savedInfo));
        setLoading(false);
    }, []);

    const handleOAuthCallback = useCallback(async (code) => {
        const redirectUri = 'http://localhost:5173/oauth/callback';
        try {
            const res = await fetch(`${API_BASE}/api/auth/oauth-exchange`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code, redirectUri })
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.error || 'OAuth exchange failed');
            }
            const data = await res.json();

            setUser(data.user);
            localStorage.setItem('horizon_dev_user', JSON.stringify(data.user));
            if (data.rapnssToken) localStorage.setItem('horizon_dev_token', data.rapnssToken);

            // Check if user is already a developer
            await refreshDeveloperInfo(data.user.id);

            return data.user;
        } catch (err) {
            console.error('[OAuth Exchange Error]', err);
            throw err;
        }
    }, []);

    /**
     * Initialise the Rapnss SDK Button inside a given container element.
     * The SDK opens a popup — no redirect needed.
     */
    const initRapnssButton = useCallback(async (containerId) => {
        await loadRapnssSDK();
        if (!window.RapnssAuth) throw new Error('RapnssAuth SDK not available');

        window.RapnssAuth.init({
            clientId: CLIENT_ID,
            // redirectUri is still required by the OAuth server even in popup mode;
            // use the same callback path so it's registered in the Rapnss app.
            redirectUri: 'http://localhost:5173/oauth/callback',
            containerId,
            onSuccess: async (data) => {
                try {
                    await handleOAuthCallback(data.code);
                } catch (e) {
                    console.error('Auth error after SDK success:', e);
                }
            },
            onError: (err) => {
                console.error('Rapnss Auth Error:', err);
            }
        });
    }, [handleOAuthCallback]);

    const logout = () => {
        setUser(null);
        setDeveloperInfo(null);
        localStorage.removeItem('horizon_dev_user');
        localStorage.removeItem('horizon_dev_info');
        localStorage.removeItem('horizon_dev_token');
    };

    const refreshDeveloperInfo = async (userId) => {
        try {
            const res = await fetch(`${API_BASE}/api/dev/dashboard?userId=${userId}`);
            if (res.ok) {
                const data = await res.json();
                // dashboard returns { developer, plugins } — store developer (with plugins inside)
                const devWithPlugins = { ...data.developer, plugins: data.plugins || [] };
                setDeveloperInfo(devWithPlugins);
                localStorage.setItem('horizon_dev_info', JSON.stringify(devWithPlugins));
                return devWithPlugins;
            }
            return null;
        } catch (e) {
            console.error('[refreshDeveloperInfo]', e);
            return null;
        }
    };

    const acceptTerms = async () => {
        if (!user) return;
        try {
            const res = await fetch(`${API_BASE}/api/dev/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ userId: user.id })
            });
            const data = await res.json();
            if (data.success) {
                const devWithPlugins = { ...data.developer, plugins: [] };
                setDeveloperInfo(devWithPlugins);
                localStorage.setItem('horizon_dev_info', JSON.stringify(devWithPlugins));
                return data.message;
            }
        } catch (err) {
            console.error('[acceptTerms]', err);
            throw err;
        }
    };

    const value = {
        user,
        developerInfo,
        loading,
        logout,
        initRapnssButton,
        handleOAuthCallback,
        refreshDeveloperInfo,
        acceptTerms,
        API_BASE
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
