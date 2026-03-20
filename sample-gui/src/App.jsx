import React, { useState, useEffect } from 'react';
import { CreditCard } from 'lucide-react'; // Import icon for plans
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import SplashScreen from './components/SplashScreen';
import Plans from './components/Plans';
import Teams from './components/Teams';
import Home from './components/Home';
import Login from './components/Login';
import Settings from './components/Settings';
import Plugins from './components/Plugins';
import Monitor from './components/Monitor';
import Feedback from './components/Feedback';
import Onboarding from './components/Onboarding';
import { usePostHog } from '@posthog/react';

function App() {
  const posthog = usePostHog();
  const [activeTab, setActiveTab] = useState('home');
  const [showSplash, setShowSplash] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(() => {
    return localStorage.getItem('horizon_onboarding_done') !== 'true';
  });
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('horizon_user');
    return saved ? JSON.parse(saved) : null;
  }); // Auth state

  useEffect(() => {
    // Load global settings on startup (e.g., dark mode)
    const initSettings = async () => {
      // Load language from localStorage first for instant app-start feedback
      const savedLang = localStorage.getItem('horizon_language');
      if (savedLang) {
        document.documentElement.setAttribute('lang', savedLang.split(' ')[0].toLowerCase());
      }

      if (window.pywebview?.api?.get_settings) {
        try {
          const settings = await window.pywebview.api.get_settings();
          
          // Apply font size globally
          if (settings.fontSize) {
            document.documentElement.style.setProperty('--font-scale', `${settings.fontSize / 50}`);
          }

          if (settings.darkMode !== undefined) {
            if (settings.darkMode) {
              document.body.classList.remove('light-mode');
            } else {
              document.body.classList.add('light-mode');
            }
          }
          
          if (settings.language) {
            localStorage.setItem('horizon_language', settings.language);
            document.documentElement.setAttribute('lang', settings.language.split(' ')[0].toLowerCase());
          }
        } catch (e) {
          console.error("Error loading startup settings:", e);
        }
      }
    };
    initSettings();
  }, []);

  useEffect(() => {
    if (user && !showSplash && !showOnboarding) {
      posthog.capture('page_view', { tab_name: activeTab });
    }
  }, [activeTab, user, showSplash, showOnboarding, posthog]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      {/* Global TopBar for window controls */}
      <TopBar 
        title={showSplash ? "Initializing" : showOnboarding ? "Onboarding" : !user ? "Login" : activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} 
        setActiveTab={user ? setActiveTab : null} 
      />

      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {showSplash ? (
          <SplashScreen onFinish={() => setShowSplash(false)} />
        ) : showOnboarding ? (
          <Onboarding onComplete={() => {
            setShowOnboarding(false);
            window.dispatchEvent(new CustomEvent('settings-updated'));
          }} />
        ) : !user ? (
          <Login onLogin={(u) => {
            setUser(u);
            localStorage.setItem('horizon_user', JSON.stringify(u));
            posthog.identify(u.id, { email: u.email, username: u.username });
            posthog.capture('user_login', { method: 'Rapnss OAuth' });
          }} />
        ) : (
          <>
            <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
            <div style={{
              flex: 1,
              backgroundColor: 'var(--bg-app)',
              padding: '20px',
              overflowY: 'auto'
            }}>
              {activeTab === 'home' && <Home />}
              {activeTab === 'teams' && <Teams />}
              {activeTab === 'plugins' && <Plugins />}
              {activeTab === 'monitor' && <Monitor />}
              {activeTab === 'settings' && <Settings user={user} />}
              {activeTab === 'plans' && <Plans />}
              {activeTab === 'feedback' && <Feedback user={user} />}
            </div>
          </>
        )}
      </div>

      <style>{`
        .card {
            background: var(--bg-panel);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
      `}</style>
    </div>
  );
}

export default App;
