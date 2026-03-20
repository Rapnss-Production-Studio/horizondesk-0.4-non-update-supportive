# Horizon Giga UI - Implementation Plan

## Overview
Create a Windows desktop transformation that gives users a macOS-like experience with AI integration.

## UI Mode Selection
On first launch, user chooses:
1. **Default Windows UI** - Standard Windows + floating overlay
2. **Horizon Giga UI** - Full desktop transformation

---

## Giga UI Components

### 1. Bottom Dock (macOS-style)
- Replaces Windows taskbar (auto-hides Windows taskbar)
- Icons: Magnified on hover
- Always-visible prompt input bar
- App icons with bounce animations

### 2. Desktop Icons
- Custom macOS-style folder icons
- Rounded rectangle style
- Hover effects

### 3. AI Prompt Bar (Always Visible)
- Centered at bottom, above dock
- Glassmorphism style
- Settings button

### 4. Mode Switcher Icon
- Desktop shortcut to toggle modes
- "Switch to Windows Mode" / "Switch to Giga UI"

---

## File Structure
```
giga-ui/
├── launcher.py           # Main entry point
├── mode_selector.py      # First-run UI selection
├── giga_mode/
│   ├── dock.html         # macOS-style dock
│   ├── dock.css
│   ├── dock.js
│   ├── prompt_bar.html   # AI prompt bar
│   └── icons/            # Custom folder icons
├── config.json           # Stores selected mode
└── switch_mode.py        # Toggle between modes
```

---

## Tasks
- [ ] Create mode selector UI
- [ ] Build macOS-style dock component
- [ ] Create custom folder icons
- [ ] Build persistent prompt bar
- [ ] Create mode switcher desktop shortcut
- [ ] Auto-hide Windows taskbar in Giga mode
- [ ] Save/load mode preference
