import { useState, useEffect } from 'react'

export default function SettingsPanel({ onClose, api }) {
    const [tab, setTab] = useState('wallpaper')
    const [wallpapers, setWallpapers] = useState([])
    const [fonts, setFonts] = useState([])
    const [config, setConfig] = useState({})
    const [activeFont, setActiveFont] = useState('')

    useEffect(() => {
        fetch(`${api}/api/wallpapers`).then(r => r.json()).then(setWallpapers).catch(() => { })
        fetch(`${api}/api/fonts`).then(r => r.json()).then(setFonts).catch(() => { })
        fetch(`${api}/api/config`).then(r => r.json()).then(c => {
            setConfig(c)
            setActiveFont(c?.theme?.font_family || 'Segoe UI')
        }).catch(() => { })
    }, [api])

    const saveConfig = (updates) => {
        const newConfig = { ...config, ...updates }
        setConfig(newConfig)
        fetch(`${api}/api/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        })
    }

    const applyWallpaper = (path) => {
        fetch(`${api}/api/theme/apply`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ wallpaper: path })
        })
    }

    const tabs = [
        { id: 'wallpaper', label: '🖼 Wallpaper', icon: '' },
        { id: 'colors', label: '🎨 Colors', icon: '' },
        { id: 'typography', label: '✏️ Typography', icon: '' },
        { id: 'window', label: '⊞ Window Style', icon: '' },
    ]

    const colorKeys = [
        { key: 'accent', label: 'Accent' },
        { key: 'bg_glass', label: 'Background' },
        { key: 'text', label: 'Text Color' },
        { key: 'border', label: 'Borders' },
    ]

    const windowStyles = [
        { id: 'default', label: 'Windows Default' },
        { id: 'macos', label: 'macOS Traffic Lights' },
        { id: 'sleek', label: 'Sleek Dots' },
        { id: 'minimal', label: 'Minimal Lines' },
    ]

    return (
        <div className="settings-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
            <div className="settings-panel">
                {/* Sidebar */}
                <div className="settings-panel__sidebar">
                    <div className="settings-panel__sidebar-title">Settings</div>
                    {tabs.map(t => (
                        <button
                            key={t.id}
                            className={`settings-panel__tab ${tab === t.id ? 'settings-panel__tab--active' : ''}`}
                            onClick={() => setTab(t.id)}
                        >
                            {t.label}
                        </button>
                    ))}
                </div>

                {/* Content */}
                <div className="settings-panel__content" style={{ position: 'relative' }}>
                    <button className="settings-panel__close" onClick={onClose}>✕</button>

                    {/* Wallpaper */}
                    {tab === 'wallpaper' && (
                        <>
                            <h2>Wallpaper</h2>
                            <div className="wallpaper-grid">
                                {wallpapers.map(w => (
                                    <div
                                        key={w.name}
                                        className="wallpaper-card"
                                        onClick={() => applyWallpaper(w.path)}
                                    >
                                        <img src={`${api}/api/wallpaper-image/${w.name}`} alt={w.name} loading="lazy" />
                                        <div className="wallpaper-card__name">{w.name}</div>
                                    </div>
                                ))}
                                {wallpapers.length === 0 && (
                                    <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>
                                        No wallpapers found in /wallpaper directory
                                    </p>
                                )}
                            </div>
                        </>
                    )}

                    {/* Colors */}
                    {tab === 'colors' && (
                        <>
                            <h2>Colors</h2>
                            <h3>Custom Overrides</h3>
                            {colorKeys.map(({ key, label }) => (
                                <div className="color-row" key={key}>
                                    <span className="color-row__label">{label}</span>
                                    <input
                                        type="color"
                                        className="color-row__swatch"
                                        defaultValue={config?.theme?.custom_colors?.[key] || '#6366f1'}
                                        onChange={(e) => {
                                            saveConfig({
                                                theme: {
                                                    ...config.theme,
                                                    custom_colors: {
                                                        ...config?.theme?.custom_colors,
                                                        [key]: e.target.value
                                                    }
                                                }
                                            })
                                        }}
                                    />
                                </div>
                            ))}
                        </>
                    )}

                    {/* Typography */}
                    {tab === 'typography' && (
                        <>
                            <h2>Typography</h2>
                            <h3>Font Family</h3>
                            <div className="font-list">
                                {fonts.map(f => (
                                    <div
                                        key={f}
                                        className={`font-item ${activeFont === f ? 'font-item--active' : ''}`}
                                        style={{ fontFamily: f }}
                                        onClick={() => {
                                            setActiveFont(f)
                                            saveConfig({
                                                theme: { ...config.theme, font_family: f }
                                            })
                                        }}
                                    >
                                        {f}
                                    </div>
                                ))}
                            </div>

                            <h3>Weight</h3>
                            {['light', 'normal', 'bold'].map(w => (
                                <label key={w} style={{
                                    display: 'flex', alignItems: 'center', gap: 8,
                                    padding: '6px 0', fontSize: 14, cursor: 'pointer'
                                }}>
                                    <input
                                        type="radio"
                                        name="weight"
                                        value={w}
                                        defaultChecked={config?.theme?.font_weight === w || (w === 'light' && !config?.theme?.font_weight)}
                                        onChange={() => saveConfig({ theme: { ...config.theme, font_weight: w } })}
                                    />
                                    {w.charAt(0).toUpperCase() + w.slice(1)}
                                </label>
                            ))}
                        </>
                    )}

                    {/* Window Style */}
                    {tab === 'window' && (
                        <>
                            <h2>Window Style</h2>
                            <h3>Control Button Design</h3>
                            {windowStyles.map(s => (
                                <label key={s.id} style={{
                                    display: 'flex', alignItems: 'center', gap: 10,
                                    padding: '10px 0', fontSize: 14, cursor: 'pointer',
                                    borderBottom: '0.5px solid var(--border)'
                                }}>
                                    <input
                                        type="radio"
                                        name="windowStyle"
                                        value={s.id}
                                        defaultChecked={config?.theme?.window_style === s.id || (s.id === 'default' && !config?.theme?.window_style)}
                                        onChange={() => saveConfig({ theme: { ...config.theme, window_style: s.id } })}
                                    />
                                    {s.label}
                                </label>
                            ))}
                            <p style={{ marginTop: 16, fontSize: 12, color: 'var(--text-muted)' }}>
                                Changes apply on restart.
                            </p>
                        </>
                    )}
                </div>
            </div>
        </div>
    )
}
