import { useState, useCallback } from 'react'
import './App.css'

// pywebview bridge
const api = () => window.pywebview?.api || null

function showToast(msg) {
  const t = document.getElementById('toast')
  if (t) {
    t.textContent = '✓ ' + msg
    t.classList.add('show')
    setTimeout(() => t.classList.remove('show'), 2200)
  }
}

const TABS = [
  { id: 'appearance', icon: '🎨', label: 'Appearance' },
  { id: 'wallpaper', icon: '🖼', label: 'Wallpaper' },
  { id: 'typography', icon: '🔤', label: 'Typography' },
  { id: 'layout', icon: '📐', label: 'Layout' },
  { id: 'icons', icon: '🎯', label: 'Icon Studio' },
]

const FONTS = [
  'Inter', 'Segoe UI', 'Roboto', 'Arial', 'Helvetica Neue',
  'Cascadia Code', 'Fira Code', 'JetBrains Mono', 'Consolas',
  'Calibri', 'Cambria', 'Georgia', 'Tahoma', 'Trebuchet MS',
  'Century Gothic', 'Palatino Linotype', 'Verdana', 'Garamond',
  'Outfit', 'Poppins'
]

const TEMPLATES = [
  { id: 'gradient', icon: '🌈', name: 'Gradient' },
  { id: 'flat', icon: '⬜', name: 'Flat' },
  { id: 'neon', icon: '💚', name: 'Neon' },
  { id: 'pastel', icon: '🩷', name: 'Pastel' },
  { id: 'metallic', icon: '⚙', name: 'Metallic' },
  { id: 'glass', icon: '🪟', name: 'Glass' },
]

// ═══ Appearance Tab ═══
function AppearanceTab() {
  const [taskbarOp, setTaskbarOp] = useState(94)
  const [iconOp, setIconOp] = useState(70)
  const [promptOp, setPromptOp] = useState(96)

  const setColor = (key, val) => {
    api()?.set_color(key, val)
    showToast('Color updated')
  }

  const setSlider = (key, val, setter) => {
    setter(val)
    api()?.set_slider(key, parseInt(val))
  }

  return (
    <div className="fade-in">
      <h2 className="page-title">Appearance</h2>
      <p className="page-desc">Customize colors and opacity of UI elements</p>

      <div className="section">
        <div className="section-title">🎨 Colors</div>
        <div className="setting-card">
          <ColorRow label="Accent Color" desc="Primary highlight" configKey="accent_color" defaultVal="#818cf8" onChange={setColor} />
          <ColorRow label="Text Color" desc="Main text color" configKey="text_color" defaultVal="#e8e8f0" onChange={setColor} />
          <ColorRow label="Panel Background" desc="Taskbar & prompt fill" configKey="panel_bg" defaultVal="#0e0e1a" onChange={setColor} />
          <ColorRow label="App Icon Color" desc="Running app labels" configKey="app_icon_color" defaultVal="#7a7a9a" onChange={setColor} />
        </div>
      </div>

      <div className="section">
        <div className="section-title">🔆 Opacity</div>
        <div className="setting-card">
          <SliderRow label="Taskbar Opacity" min={50} max={100} value={taskbarOp} unit="%"
            onChange={v => setSlider('taskbar_opacity', v, setTaskbarOp)} />
          <SliderRow label="App Icon Opacity" min={30} max={100} value={iconOp} unit="%"
            onChange={v => setSlider('app_icon_opacity', v, setIconOp)} />
          <SliderRow label="Prompt Opacity" min={50} max={100} value={promptOp} unit="%"
            onChange={v => setSlider('prompt_opacity', v, setPromptOp)} />
        </div>
      </div>
    </div>
  )
}

// ═══ Wallpaper Tab ═══
function WallpaperTab() {
  return (
    <div className="fade-in">
      <h2 className="page-title">Wallpaper</h2>
      <p className="page-desc">Change your desktop wallpaper</p>

      <div className="section">
        <div className="section-title">🖼 Current Wallpaper</div>
        <div className="icon-preview-area">
          <div className="icon-preview-box" style={{ fontSize: 32 }}>🏔️</div>
          <div className="icon-preview-info">
            <h4>Desktop Wallpaper</h4>
            <p>Click Browse to select a new image from your files</p>
          </div>
        </div>
      </div>

      <div className="btn-group">
        <button className="btn btn-primary" onClick={() => { api()?.browse_wallpaper(); showToast('Opening file picker...') }}>
          📁 Browse Image
        </button>
        <button className="btn btn-danger" onClick={() => { api()?.restore_wallpaper(); showToast('Wallpaper restored') }}>
          ↩ Restore Default
        </button>
      </div>
    </div>
  )
}

// ═══ Typography Tab ═══
function TypographyTab() {
  const [selected, setSelected] = useState('Segoe UI')

  return (
    <div className="fade-in">
      <h2 className="page-title">Typography</h2>
      <p className="page-desc">Choose the font family for the UI</p>

      <div className="section">
        <div className="section-title">🔤 Font Family</div>
        <div className="font-list">
          {FONTS.map(f => (
            <div key={f}
              className={`font-item ${selected === f ? 'selected' : ''}`}
              style={{ fontFamily: f }}
              onClick={() => setSelected(f)}>
              {f}
            </div>
          ))}
        </div>

        <div className="font-preview" style={{ fontFamily: selected }}>
          The quick brown fox jumps over the lazy dog — {selected}
        </div>

        <div className="btn-group">
          <button className="btn btn-primary" onClick={() => { api()?.apply_font(selected); showToast('Font applied: ' + selected) }}>
            ✓ Apply Font
          </button>
        </div>
      </div>
    </div>
  )
}

// ═══ Layout Tab ═══
function LayoutTab() {
  const [vals, setVals] = useState({
    taskbar_height: 36,
    prompt_width: 640,
    prompt_height: 50,
    prompt_offset: 20,
  })

  const update = (key, val) => {
    setVals(prev => ({ ...prev, [key]: val }))
    api()?.set_slider(key, parseInt(val))
  }

  const reset = () => {
    setVals({ taskbar_height: 36, prompt_width: 640, prompt_height: 50, prompt_offset: 20 })
    api()?.reset_layout()
    showToast('Layout reset to defaults')
  }

  return (
    <div className="fade-in">
      <h2 className="page-title">Layout</h2>
      <p className="page-desc">Adjust panel dimensions and positioning</p>

      <div className="section">
        <div className="section-title">📐 Panel Dimensions</div>
        <div className="setting-card">
          <SliderRow label="Taskbar Height" min={28} max={52} value={vals.taskbar_height} unit="px"
            onChange={v => update('taskbar_height', v)} />
          <SliderRow label="Prompt Width" min={400} max={900} value={vals.prompt_width} unit="px"
            onChange={v => update('prompt_width', v)} />
          <SliderRow label="Prompt Height" min={40} max={70} value={vals.prompt_height} unit="px"
            onChange={v => update('prompt_height', v)} />
          <SliderRow label="Bottom Offset" min={10} max={80} value={vals.prompt_offset} unit="px"
            onChange={v => update('prompt_offset', v)} />
        </div>
      </div>

      <div className="btn-group">
        <button className="btn btn-secondary" onClick={reset}>↩ Reset to Defaults</button>
      </div>
    </div>
  )
}

// ═══ Icon Studio Tab ═══
function IconStudioTab() {
  const [selectedTemplate, setSelectedTemplate] = useState('gradient')
  const [iconColor, setIconColor] = useState('#818cf8')

  return (
    <div className="fade-in">
      <h2 className="page-title">Icon Studio</h2>
      <p className="page-desc">Design and apply custom folder icons</p>

      <div className="section">
        <div className="section-title">🎯 Template Style</div>
        <div className="template-grid">
          {TEMPLATES.map(t => (
            <div key={t.id}
              className={`template-card ${selectedTemplate === t.id ? 'selected' : ''}`}
              onClick={() => setSelectedTemplate(t.id)}>
              <div className="template-icon">{t.icon}</div>
              <div className="template-name">{t.name}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="section">
        <div className="section-title">🎨 Icon Color</div>
        <div className="setting-card">
          <div className="setting-row">
            <div className="setting-info">
              <div className="setting-label">Primary Color</div>
              <div className="setting-desc">Base color for icon template</div>
            </div>
            <div className="color-swatch" style={{ background: iconColor }}>
              <input type="color" value={iconColor} onChange={e => setIconColor(e.target.value)} />
            </div>
          </div>
        </div>
      </div>

      <div className="section">
        <div className="section-title">👁 Preview</div>
        <div className="icon-preview-area">
          <div className="icon-preview-box">📁</div>
          <div className="icon-preview-info">
            <h4>{TEMPLATES.find(t => t.id === selectedTemplate)?.name} Style</h4>
            <p>Color: {iconColor} — Click Generate to preview</p>
          </div>
        </div>
      </div>

      <div className="btn-group">
        <button className="btn btn-secondary" onClick={() => {
          api()?.generate_icon_preview(selectedTemplate, iconColor)
          showToast('Generating preview...')
        }}>
          👁 Generate Preview
        </button>
        <button className="btn btn-primary" onClick={() => {
          api()?.apply_icon_template(selectedTemplate, iconColor)
          showToast('Applying to all folders...')
        }}>
          ✓ Apply to Folders
        </button>
        <button className="btn btn-danger" onClick={() => {
          api()?.restore_default_icons()
          showToast('Icons restored')
        }}>
          ↩ Restore
        </button>
      </div>
    </div>
  )
}

// ═══ Reusable Components ═══
function ColorRow({ label, desc, configKey, defaultVal, onChange }) {
  const [color, setColor] = useState(defaultVal)
  return (
    <div className="setting-row">
      <div className="setting-info">
        <div className="setting-label">{label}</div>
        <div className="setting-desc">{desc}</div>
      </div>
      <div className="color-swatch" style={{ background: color }}>
        <input type="color" value={color} onChange={e => { setColor(e.target.value); onChange(configKey, e.target.value) }} />
      </div>
    </div>
  )
}

function SliderRow({ label, min, max, value, unit, onChange }) {
  return (
    <div className="setting-row">
      <div className="setting-info">
        <div className="setting-label">{label}</div>
      </div>
      <div className="slider-wrap">
        <input type="range" min={min} max={max} value={value}
          onChange={e => onChange(Number(e.target.value))} />
        <span className="slider-value">{value}{unit}</span>
      </div>
    </div>
  )
}

// ═══ Main App ═══
export default function App() {
  const [activeTab, setActiveTab] = useState('appearance')

  const renderTab = useCallback(() => {
    switch (activeTab) {
      case 'appearance': return <AppearanceTab />
      case 'wallpaper': return <WallpaperTab />
      case 'typography': return <TypographyTab />
      case 'layout': return <LayoutTab />
      case 'icons': return <IconStudioTab />
      default: return <AppearanceTab />
    }
  }, [activeTab])

  return (
    <>
      {/* Header */}
      <div className="header">
        <div className="header-left">
          <div className="header-logo">✦</div>
          <div>
            <div className="header-title">Horizon Settings</div>
            <div className="header-subtitle">Giga UI Configuration</div>
          </div>
        </div>
        <button className="header-close" onClick={() => api()?.close_settings()} title="Close">✕</button>
      </div>

      {/* Body */}
      <div className="app-layout">
        {/* Sidebar */}
        <nav className="sidebar">
          <div className="sidebar-section">Settings</div>
          {TABS.map(tab => (
            <button key={tab.id}
              className={`sidebar-item ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}>
              <span className="icon">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>

        {/* Content */}
        <main className="content" key={activeTab}>
          {renderTab()}
        </main>
      </div>

      {/* Status */}
      <div className="status-bar">
        <div><span className="status-dot"></span> Horizon Desktop Active</div>
        <div>v2.0 · Giga UI</div>
      </div>

      {/* Toast */}
      <div className="toast" id="toast"></div>
    </>
  )
}
