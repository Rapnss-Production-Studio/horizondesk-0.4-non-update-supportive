import React, { useState, useEffect } from 'react';
import { 
    Moon, Sun, User, Cpu, Save, LogOut, LayoutDashboard, Monitor, 
    ShieldCheck, Bell, Zap, Link, HardDrive, Check, Image as ImageIcon,
    MessageSquare, Settings as SettingsIcon, AlertCircle 
} from 'lucide-react';
import { usePostHog } from '@posthog/react';

const Settings = ({ user }) => {
    const posthog = usePostHog();
    const [activeTab, setActiveTab] = useState('appearance');
    const [saving, setSaving] = useState(false);
    const [appVersion, setAppVersion] = useState('0.2');

    // Form State (matching the UI mockup)
    const [darkMode, setDarkMode] = useState(true);
    const [notificationsEnabled, setNotificationsEnabled] = useState(true);
    const [automationEnabled, setAutomationEnabled] = useState(true);
    
    // Appearance Tab
    const [uiDensity, setUiDensity] = useState('comfortable');
    const [accentColor, setAccentColor] = useState('#10b981'); // Emerald
    const [fontSize, setFontSize] = useState(50); // 0-100 range
    const [animationsEnabled, setAnimationsEnabled] = useState(true);

    // Workspace settings
    const [workspaceName, setWorkspaceName] = useState('Horizon Desk');
    const [defaultFolder, setDefaultFolder] = useState('/projects/');
    const [language, setLanguage] = useState('English (US)');
    const [timezone, setTimezone] = useState('United States (UTC-4:00)');
    const [country, setCountry] = useState('United States');

    // Automation Tab
    const [enableBackgroundAgents, setEnableBackgroundAgents] = useState(true);
    const [autoTaskExecution, setAutoTaskExecution] = useState(false);
    const [taskRetryLimit, setTaskRetryLimit] = useState(true);
    const [agentName, setAgentName] = useState('Horizon Agent');
    const [model, setModel] = useState('Rapnss Inference Engine');
    const [customApiUrl, setCustomApiUrl] = useState('');
    const [groqApiKey, setGroqApiKey] = useState('');
    const [canvaApiKey, setCanvaApiKey] = useState('');

    // Notifications Tab
    const [desktopNotifications, setDesktopNotifications] = useState(true);
    const [taskCompletionAlerts, setTaskCompletionAlerts] = useState(true);
    const [agentActivityAlerts, setAgentActivityAlerts] = useState(true);
    const [dailySummaryEmail, setDailySummaryEmail] = useState(false);

    // Save feedback
    const [saveMessage, setSaveMessage] = useState('');

    useEffect(() => {
        posthog.capture('settings_opened');
        
        // Load initial settings
        const loadSettings = async () => {
            if (window.pywebview?.api) {
                try {
                    const settings = await window.pywebview.api.get_settings();
                    if (settings.darkMode !== undefined) setDarkMode(settings.darkMode);
                    if (settings.agentName) setAgentName(settings.agentName);
                    if (settings.model) setModel(settings.model);
                    if (settings.customApiUrl !== undefined) setCustomApiUrl(settings.customApiUrl);
                    if (settings.groqApiKey !== undefined) setGroqApiKey(settings.groqApiKey);
                    if (settings.canvaApiKey !== undefined) setCanvaApiKey(settings.canvaApiKey);
                    if (settings.accentColor) setAccentColor(settings.accentColor);
                    if (settings.uiDensity) setUiDensity(settings.uiDensity);
                    if (settings.fontSize !== undefined) setFontSize(settings.fontSize);
                    if (settings.animationsEnabled !== undefined) setAnimationsEnabled(settings.animationsEnabled);
                    if (settings.workspaceName) setWorkspaceName(settings.workspaceName);
                    if (settings.language) setLanguage(settings.language);
                    if (settings.timezone) setTimezone(settings.timezone);
                    if (settings.country) setCountry(settings.country);
                    if (settings.notificationsEnabled !== undefined) setNotificationsEnabled(settings.notificationsEnabled);
                    if (settings.automationEnabled !== undefined) setAutomationEnabled(settings.automationEnabled);
                    if (settings.enableBackgroundAgents !== undefined) setEnableBackgroundAgents(settings.enableBackgroundAgents);
                    if (settings.autoTaskExecution !== undefined) setAutoTaskExecution(settings.autoTaskExecution);
                    if (settings.taskRetryLimit !== undefined) setTaskRetryLimit(settings.taskRetryLimit);
                    if (settings.desktopNotifications !== undefined) setDesktopNotifications(settings.desktopNotifications);
                    if (settings.taskCompletionAlerts !== undefined) setTaskCompletionAlerts(settings.taskCompletionAlerts);
                    if (settings.agentActivityAlerts !== undefined) setAgentActivityAlerts(settings.agentActivityAlerts);
                    if (settings.dailySummaryEmail !== undefined) setDailySummaryEmail(settings.dailySummaryEmail);

                    // Apply theme immediately on load
                    applyTheme(settings.darkMode, settings.accentColor || '#10b981', settings.fontSize);

                    // Get Version
                    const version = await window.pywebview.api.get_app_version();
                    setAppVersion(version);
                } catch (e) {
                    console.error('Failed to load settings:', e);
                }
            }
        };
        loadSettings();
    }, [posthog]);

    const applyTheme = (isDark, color, fSize) => {
        if (isDark) {
            document.body.classList.remove('light-mode');
        } else {
            document.body.classList.add('light-mode');
        }
        document.documentElement.style.setProperty('--accent', color);
        if (fSize !== undefined) {
            document.documentElement.style.setProperty('--font-scale', `${fSize / 50}`);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        setSaveMessage('');
        posthog.capture('settings_saved', { tab: activeTab, darkMode });
        
        applyTheme(darkMode, accentColor, fontSize);

        if (window.pywebview?.api) {
            try {
                const settings = {
                    darkMode,
                    agentName,
                    model,
                    customApiUrl,
                    groqApiKey,
                    canvaApiKey,
                    accentColor,
                    uiDensity,
                    fontSize,
                    animationsEnabled,
                    workspaceName,
                    language,
                    timezone,
                    country,
                    notificationsEnabled,
                    automationEnabled,
                    enableBackgroundAgents,
                    autoTaskExecution,
                    taskRetryLimit,
                    desktopNotifications,
                    taskCompletionAlerts,
                    agentActivityAlerts,
                    dailySummaryEmail,
                };
                const res = await window.pywebview.api.save_settings(JSON.stringify(settings));
                if (res.success) {
                    setSaveMessage('✅ Settings saved successfully!');
                } else {
                    setSaveMessage('❌ Failed to save: ' + res.error);
                }
            } catch (e) {
                setSaveMessage('❌ Error: ' + e);
            }
        } else {
            setSaveMessage('✅ Settings applied (demo mode — not persisted)');
        }
        
        setTimeout(() => { setSaving(false); setSaveMessage(''); }, 3000);
    };

    // Sidebar navigation items
    const navGroups = [
        {
            items: [
                { id: 'appearance', icon: <Monitor size={18} />, label: 'Appearance' },
                { id: 'workspace', icon: <LayoutDashboard size={18} />, label: 'Workspace' },
                { id: 'automation', icon: <Cpu size={18} />, label: 'Automation' },
                { id: 'notifications', icon: <Bell size={18} />, label: 'Notifications' },
                { id: 'security', icon: <ShieldCheck size={18} />, label: 'Security' },
                { id: 'integrations', icon: <Link size={18} />, label: 'Integrations' },
                { id: 'data', icon: <HardDrive size={18} />, label: 'Data & Storage' },
                { id: 'system', icon: <SettingsIcon size={18} />, label: 'System' },
            ]
        }
    ];

    const ToggleSwitch = ({ checked, onChange }) => (
        <div 
            onClick={() => onChange(!checked)}
            style={{
                width: '44px', height: '24px', backgroundColor: checked ? 'var(--accent)' : 'var(--border-subtle)',
                borderRadius: '12px', position: 'relative', cursor: 'pointer', transition: 'background 0.3s'
            }}
        >
            <div style={{
                width: '20px', height: '20px', backgroundColor: 'var(--bg-app)', borderRadius: '50%',
                position: 'absolute', top: '2px', left: checked ? '22px' : '2px', transition: 'left 0.3s',
                boxShadow: '0 1px 3px rgba(0,0,0,0.2)'
            }} />
        </div>
    );

    // Mockup Colors
    const colors = ['#475569', '#3b82f6', '#0ea5e9', '#10b981', '#059669', '#8b5cf6', '#d946ef', '#f43f5e'];

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', padding: '0 20px 20px 20px', overflowY: 'hidden' }}>
            
            {/* Top Quick Settings Bar */}
            <div style={{ display: 'flex', gap: '15px', marginBottom: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', background: 'var(--bg-panel)', padding: '8px 16px', borderRadius: '100px', border: '1px solid var(--border-subtle)' }}>
                    <span style={{ fontSize: '14px', display: 'flex', alignItems: 'center', gap: '6px' }}><Moon size={16}/> Dark Mode</span>
                    <ToggleSwitch checked={darkMode} onChange={setDarkMode} />
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', background: 'var(--bg-panel)', padding: '8px 16px', borderRadius: '100px', border: '1px solid var(--border-subtle)' }}>
                    <span style={{ fontSize: '14px', display: 'flex', alignItems: 'center', gap: '6px' }}><Bell size={16}/> Notifications</span>
                    <ToggleSwitch checked={notificationsEnabled} onChange={setNotificationsEnabled} />
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', background: 'var(--bg-panel)', padding: '8px 16px', borderRadius: '100px', border: '1px solid var(--border-subtle)' }}>
                    <span style={{ fontSize: '14px', display: 'flex', alignItems: 'center', gap: '6px' }}><Zap size={16}/> Automation</span>
                    <ToggleSwitch checked={automationEnabled} onChange={setAutomationEnabled} />
                </div>
            </div>

            <div style={{ display: 'flex', gap: '30px', flex: 1, minHeight: 0 }}>
                {/* Settings Sidebar */}
                <div style={{ width: '240px', display: 'flex', flexDirection: 'column', gap: '20px', overflowY: 'auto', paddingRight: '10px' }}>
                    
                    {/* Active Section Headers */}
                    <div style={{ fontSize: '18px', fontWeight: 600, paddingLeft: '10px', marginBottom: '-10px' }}>
                        {navGroups[0].items.find(i => i.id === activeTab)?.label}
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        {navGroups[0].items.map(item => (
                            <button 
                                key={item.id}
                                onClick={() => setActiveTab(item.id)}
                                style={{
                                    display: 'flex', alignItems: 'center', gap: '10px', padding: '10px 16px',
                                    borderRadius: '8px', border: 'none', background: activeTab === item.id ? 'var(--bg-hover)' : 'transparent',
                                    color: activeTab === item.id ? 'var(--text-main)' : 'var(--text-secondary)',
                                    fontWeight: activeTab === item.id ? '600' : '500', cursor: 'pointer',
                                    textAlign: 'left', transition: 'all 0.2s',
                                    borderLeft: activeTab === item.id ? '3px solid var(--accent)' : '3px solid transparent'
                                }}
                            >
                                {item.icon}
                                {item.label}
                            </button>
                        ))}
                    </div>

                    <div style={{ borderTop: '1px solid var(--border-subtle)', margin: '10px 0' }} />
                    
                    {/* Account preview in sidebar */}
                    <div style={{ padding: '10px', background: 'var(--bg-panel)', borderRadius: '12px', border: '1px solid var(--border-subtle)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'var(--accent)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
                                {(user?.name || user?.username || 'U')[0].toUpperCase()}
                            </div>
                            <div style={{ flex: 1, overflow: 'hidden' }}>
                                <div style={{ fontWeight: 600, fontSize: '14px', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>
                                    {user?.username || user?.name || 'User'}
                                </div>
                                <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Pro Plan</div>
                            </div>
                        </div>
                        <button 
                            onClick={() => { localStorage.removeItem('horizon_user'); window.location.reload(); }}
                            style={{ width: '100%', marginTop: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', background: 'transparent', border: '1px solid var(--border-subtle)', padding: '6px', borderRadius: '6px', color: 'var(--red)', cursor: 'pointer', fontSize: '13px' }}
                        >
                            <LogOut size={14}/> Sign Out
                        </button>
                    </div>

                </div>

                {/* Settings Content Area */}
                <div style={{ flex: 1, overflowY: 'auto', paddingRight: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    
                    {activeTab === 'appearance' && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                                <div>
                                    <div style={{ fontWeight: 600, marginBottom: '10px' }}>Theme</div>
                                    <div style={{ display: 'flex', gap: '10px' }}>
                                        <button onClick={() => setDarkMode(false)} style={{ flex: 1, padding: '10px', borderRadius: '8px', border: !darkMode ? '2px solid var(--accent)' : '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--text-main)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', cursor: 'pointer', fontWeight: !darkMode ? 600 : 400 }}>
                                            <Sun size={18} /> Light
                                        </button>
                                        <button onClick={() => setDarkMode(true)} style={{ flex: 1, padding: '10px', borderRadius: '8px', border: darkMode ? '2px solid var(--accent)' : '1px solid var(--border-subtle)', background: 'var(--bg-panel)', color: 'var(--text-main)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', cursor: 'pointer', fontWeight: darkMode ? 600 : 400 }}>
                                            <Moon size={18} /> Dark
                                        </button>
                                        <button style={{ flex: 1, padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'transparent', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', cursor: 'pointer' }}>
                                            <Monitor size={18} /> System
                                        </button>
                                    </div>
                                </div>

                                <div>
                                    <div style={{ fontWeight: 600, marginBottom: '10px' }}>UI Density</div>
                                    <div style={{ display: 'flex', gap: '10px' }}>
                                        <button onClick={() => setUiDensity('comfortable')} style={{ padding: '8px 16px', borderRadius: '100px', border: uiDensity === 'comfortable' ? 'none' : '1px solid var(--border-subtle)', background: uiDensity === 'comfortable' ? 'var(--accent)' : 'transparent', color: uiDensity === 'comfortable' ? 'white' : 'var(--text-main)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                            {uiDensity === 'comfortable' && <Check size={14}/>} Comfortable
                                        </button>
                                        <button onClick={() => setUiDensity('compact')} style={{ padding: '8px 16px', borderRadius: '100px', border: uiDensity === 'compact' ? 'none' : '1px solid var(--border-subtle)', background: uiDensity === 'compact' ? 'var(--accent)' : 'transparent', color: uiDensity === 'compact' ? 'white' : 'var(--text-main)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                            {uiDensity === 'compact' && <Check size={14}/>} Compact
                                        </button>
                                    </div>
                                </div>

                                <div>
                                    <div style={{ fontWeight: 600, marginBottom: '10px' }}>Accent Color</div>
                                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center', background: 'var(--bg-app)', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                                        {colors.map(color => (
                                            <div key={color} onClick={() => setAccentColor(color)} style={{ width: '28px', height: '28px', borderRadius: '50%', background: color, cursor: 'pointer', border: accentColor === color ? '2px solid white' : 'none', outline: accentColor === color ? `2px solid ${color}` : 'none' }} />
                                        ))}
                                        <div style={{ flex: 1 }} />
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--bg-panel)', padding: '4px 10px', borderRadius: '6px' }}>
                                            <div style={{ width: '12px', height: '12px', background: accentColor, borderRadius: '2px' }}/>
                                            <span style={{ fontSize: '13px', position: 'relative', top: '1px' }}>{accentColor.toUpperCase()}</span>
                                        </div>
                                    </div>
                                </div>

                                <div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                                        <span style={{ fontWeight: 600 }}>Font Size</span>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                                        <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Small</span>
                                        <input type="range" min="0" max="100" value={fontSize} onChange={e => setFontSize(e.target.value)} style={{ flex: 1, accentColor: 'var(--accent)' }} />
                                        <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Large</span>
                                    </div>
                                </div>

                                <div style={{ borderTop: '1px solid var(--border-subtle)', margin: '5px 0' }} />
                                
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <Zap size={18} color="var(--text-secondary)" /> Animations
                                    </span>
                                    <ToggleSwitch checked={animationsEnabled} onChange={setAnimationsEnabled} />
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'workspace' && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                                <div>
                                    <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '14px' }}>Workspace name:</label>
                                    <input type="text" value={workspaceName} onChange={e => setWorkspaceName(e.target.value)} style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--text-main)' }} />
                                </div>
                                
                                <div>
                                    <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '14px' }}>Workspace Logo:</label>
                                    <div style={{ display: 'flex', gap: '15px' }}>
                                        <div style={{ width: '120px', height: '60px', borderRadius: '8px', background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 600, fontSize: '12px' }}>
                                            <img src="logo.ico" style={{ width: 16, height: 16, marginRight: 6 }}/> Horizon Desk
                                        </div>
                                        <button style={{ padding: '0 20px', borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--text-main)', cursor: 'pointer', fontWeight: 500 }}>
                                            Upload New Logo
                                        </button>
                                    </div>
                                </div>

                                <div>
                                    <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '14px' }}>Default Project Folder:</label>
                                    <select value={defaultFolder} onChange={e => setDefaultFolder(e.target.value)} style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--text-main)' }}>
                                        <option value="/projects/">/projects/</option>
                                        <option value="/documents/">/documents/</option>
                                        <option value="/downloads/">/downloads/</option>
                                    </select>
                                </div>

                                <div>
                                    <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '14px' }}>Default Language:</label>
                                    <select value={language} onChange={e => setLanguage(e.target.value)} style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--text-main)' }}>
                                        <option>English (US)</option>
                                        <option>Spanish (ES)</option>
                                        <option>French (FR)</option>
                                        <option>German (DE)</option>
                                    </select>
                                </div>

                                <div>
                                    <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '14px' }}>Country:</label>
                                    <select value={country} onChange={e => setCountry(e.target.value)} style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--text-main)' }}>
                                        <option>United States</option>
                                        <option>United Kingdom</option>
                                        <option>India</option>
                                        <option>Canada</option>
                                        <option>Australia</option>
                                    </select>
                                </div>

                                <div>
                                    <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '14px' }}>Region & Timezone:</label>
                                    <select value={timezone} onChange={e => setTimezone(e.target.value)} style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--text-main)' }}>
                                        <option>United States (UTC-4:00)</option>
                                        <option>United Kingdom (UTC+0:00)</option>
                                        <option>India (UTC+5:30)</option>
                                        <option>Japan (UTC+9:00)</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'automation' && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                            <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}><MessageSquare size={18}/> Enable background agents</span>
                                    <ToggleSwitch checked={enableBackgroundAgents} onChange={setEnableBackgroundAgents} />
                                </div>
                                <div style={{ borderTop: '1px solid var(--border-subtle)' }} />
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}><Check size={18}/> Auto Task Execution</span>
                                    <ToggleSwitch checked={autoTaskExecution} onChange={setAutoTaskExecution} />
                                </div>
                                <div style={{ borderTop: '1px solid var(--border-subtle)' }} />
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}><AlertCircle size={18}/> Task Retry Limit</span>
                                    <ToggleSwitch checked={taskRetryLimit} onChange={setTaskRetryLimit} />
                                </div>
                            </div>
                            
                            <div className="card">
                                <h3 style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <Cpu size={20} /> AI Providers
                                </h3>
                                <div style={{ marginBottom: '15px' }}>
                                    <label style={{ display: 'block', marginBottom: '5px', color: 'var(--text-secondary)' }}>Agent Name</label>
                                    <input type="text" value={agentName} onChange={e => setAgentName(e.target.value)} style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)', backgroundColor: 'var(--bg-app)', color: 'var(--text-main)' }} />
                                </div>
                                <div style={{ marginBottom: '15px' }}>
                                    <label style={{ display: 'block', marginBottom: '5px', color: 'var(--text-secondary)' }}>Inference Provider</label>
                                    <select value={model} onChange={e => setModel(e.target.value)} style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)', backgroundColor: 'var(--bg-app)', color: 'var(--text-main)' }}>
                                        <option value="Rapnss Inference Engine">Rapnss Inference Engine (Default)</option>
                                        <option value="Groq">Groq (Fast, Free Tier)</option>
                                        <option value="Custom">Custom API Endpoint</option>
                                    </select>
                                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '5px' }}>
                                        {model === 'Rapnss Inference Engine' && '✅ Using Rapnss built-in inference — no API key needed.'}
                                        {model === 'Groq' && '⚡ Groq provides ultra-fast inference. Enter your Groq API key below.'}
                                        {model === 'Custom' && '🔧 Enter your custom OpenAI-compatible API endpoint below.'}
                                    </div>
                                </div>
                                {model === 'Groq' && (
                                    <div style={{ marginBottom: '15px' }}>
                                        <label style={{ display: 'block', marginBottom: '5px', color: 'var(--text-secondary)' }}>Groq API Key</label>
                                        <input type="password" value={groqApiKey} onChange={e => setGroqApiKey(e.target.value)} placeholder="gsk_..." style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)', backgroundColor: 'var(--bg-app)', color: 'var(--text-main)' }} />
                                    </div>
                                )}
                                {model === 'Custom' && (
                                    <div style={{ marginBottom: '15px' }}>
                                        <label style={{ display: 'block', marginBottom: '5px', color: 'var(--text-secondary)' }}>Custom API Base URL</label>
                                        <input type="text" value={customApiUrl} onChange={e => setCustomApiUrl(e.target.value)} placeholder="https://api.example.com/v1" style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)', backgroundColor: 'var(--bg-app)', color: 'var(--text-main)' }} />
                                    </div>
                                )}
                                <div style={{ marginTop: '5px' }}>
                                    <label style={{ display: 'block', marginBottom: '5px', color: 'var(--text-secondary)' }}>Canva API Key (Optional — for design tasks)</label>
                                    <input type="password" value={canvaApiKey} onChange={e => setCanvaApiKey(e.target.value)} placeholder="Enter base64 basic auth string for MCP" style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)', backgroundColor: 'var(--bg-app)', color: 'var(--text-main)' }} />
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'notifications' && (
                        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}><Monitor size={18}/> Desktop Notifications</span>
                                <ToggleSwitch checked={desktopNotifications} onChange={setDesktopNotifications} />
                            </div>
                            <div style={{ borderTop: '1px solid var(--border-subtle)' }} />
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}><Bell size={18}/> Task Completion Alerts</span>
                                <ToggleSwitch checked={taskCompletionAlerts} onChange={setTaskCompletionAlerts} />
                            </div>
                            <div style={{ borderTop: '1px solid var(--border-subtle)' }} />
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}><Cpu size={18}/> Agent Activity Alerts</span>
                                <ToggleSwitch checked={agentActivityAlerts} onChange={setAgentActivityAlerts} />
                            </div>
                            <div style={{ borderTop: '1px solid var(--border-subtle)' }} />
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>📧 Daily Summary Email</span>
                                <ToggleSwitch checked={dailySummaryEmail} onChange={setDailySummaryEmail} />
                            </div>
                            <div style={{ borderTop: '1px solid var(--border-subtle)' }} />
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>🔔 Notification Sound</span>
                                <button style={{ background: 'var(--bg-app)', border: '1px solid var(--border-subtle)', padding: '4px 12px', borderRadius: '6px', color: 'var(--text-main)' }}>Edit</button>
                            </div>
                        </div>
                    )}

                    {activeTab === 'security' && (
                        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 500 }}><Monitor size={18}/> GitHub</span>
                                <button style={{ background: 'var(--bg-app)', border: '1px solid var(--border-subtle)', padding: '6px 16px', borderRadius: '6px', color: 'var(--text-main)', cursor: 'pointer' }}>Connect</button>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 500 }}><HardDrive size={18}/> Google Drive</span>
                                <button style={{ background: 'var(--bg-app)', border: '1px solid var(--border-subtle)', padding: '6px 16px', borderRadius: '6px', color: 'var(--text-main)', cursor: 'pointer' }}>Connect</button>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 500 }}><MessageSquare size={18}/> Telegram</span>
                                <button style={{ background: 'var(--bg-app)', border: '1px solid var(--border-subtle)', padding: '6px 16px', borderRadius: '6px', color: 'var(--text-main)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}><SettingsIcon size={14}/> Edit</button>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 500 }}><Link size={18}/> Webhooks</span>
                                <button style={{ background: 'var(--accent)', border: 'none', padding: '6px 16px', borderRadius: '6px', color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}><Save size={14}/> Save Changes</button>
                            </div>
                        </div>
                    )}

                    {activeTab === 'system' && (
                        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                            <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <SettingsIcon size={20} /> Version & Updates
                            </h3>
                            <div style={{ padding: '15px', background: 'var(--bg-app)', borderRadius: '12px', border: '1px solid var(--border-subtle)' }}>
                                <div style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '5px' }}>Current Version</div>
                                <div style={{ fontSize: '20px', fontWeight: 600 }}>Horizon Desk v{appVersion}</div>
                            </div>

                            <button
                                onClick={async () => {
                                    if (window.pywebview?.api) {
                                        try {
                                            const res = await window.pywebview.api.check_for_updates();
                                            if (res.success && res.updateAvailable) {
                                                if (window.confirm(`Update Available: v${res.latest}\n${res.release_notes}\n\nInstall now?`)) {
                                                    await window.pywebview.api.apply_update_now();
                                                }
                                            } else if (res.success) {
                                                alert("You are up to date!");
                                            } else {
                                                alert("Error checking for updates: " + res.error);
                                            }
                                        } catch (e) {
                                            alert("Error contacting updater API: " + e);
                                        }
                                    } else {
                                        alert("Updater not available in demo block.");
                                    }
                                }}
                                style={{
                                    padding: '12px 20px', borderRadius: '8px', border: '1px solid var(--accent)', background: 'transparent', color: 'var(--accent)', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px'
                                }}>
                                <LogOut size={16} /> Check for Updates
                            </button>
                        </div>
                    )}
                    
                    {/* Placeholder for un-implemented tabs */}
                    {['integrations', 'data'].includes(activeTab) && (
                        <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '200px', color: 'var(--text-secondary)' }}>
                            Configuration options for {navGroups[0].items.find(i => i.id === activeTab)?.label} will appear here.
                        </div>
                    )}
                    
                </div>
            </div>
            
            {/* Sticky Save Footer */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto', paddingTop: '15px', borderTop: '1px solid var(--border-subtle)', gap: '15px' }}>
                <div style={{ fontSize: '13px' }}>
                    {saveMessage ? (
                        <span style={{ color: saveMessage.startsWith('✅') ? 'var(--green)' : 'var(--red)', fontWeight: 600 }}>{saveMessage}</span>
                    ) : (
                        <span style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <Monitor size={16}/> Theme & accent colors apply immediately on save.
                        </span>
                    )}
                </div>
                
                <button
                    onClick={handleSave}
                    disabled={saving}
                    style={{
                        padding: '10px 24px', borderRadius: '100px', border: 'none', cursor: saving ? 'default' : 'pointer',
                        backgroundColor: 'var(--accent)', color: 'white', fontWeight: 'bold', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px',
                        opacity: saving ? 0.7 : 1, transition: 'all 0.2s', boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)', whiteSpace: 'nowrap'
                    }}
                >
                    <Save size={18} /> {saving ? 'Saving...' : 'Save Changes'}
                </button>
            </div>
        </div>
    );
};

export default Settings;
