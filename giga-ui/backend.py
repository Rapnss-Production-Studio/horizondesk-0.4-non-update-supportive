"""
Horizon Giga UI - Python Backend
FastAPI WebSocket server for React frontend.
Handles: Agent communication, theme config, running windows, system fonts.
"""

import asyncio
import base64
import io
import json
import os
import sys
import subprocess
import threading
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import uvicorn

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
GIGA_UI_DIR = Path(__file__).parent
HORIZON_DIR = Path.home() / "AppData" / "Local" / "HorizonDesk"
CONFIG_FILE = HORIZON_DIR / "config.json"
WALLPAPER_DIR = PROJECT_ROOT / "wallpaper"
ASSETS_DIR = PROJECT_ROOT / "assets"

# Add project root for imports
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(GIGA_UI_DIR) not in sys.path:
    sys.path.insert(0, str(GIGA_UI_DIR))

# --- Agent Process Manager ---
class AgentProcess:
    """Manages the main.py subprocess"""
    def __init__(self):
        self.process = None
        self.ws_clients = []
        self._reader_thread = None
    
    def start(self):
        main_py = PROJECT_ROOT / "main.py"
        if not main_py.exists():
            return
        self.process = subprocess.Popen(
            [sys.executable, str(main_py)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=str(PROJECT_ROOT),
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        self._reader_thread = threading.Thread(target=self._read_output, daemon=True)
        self._reader_thread.start()
    
    def _read_output(self):
        """Read stdout char by char and broadcast to WebSocket clients"""
        import re
        ansi_re = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        try:
            while self.process and self.process.poll() is None:
                char = self.process.stdout.read(1)
                if char:
                    clean = ansi_re.sub('', char)
                    if clean:
                        for ws_send in self.ws_clients:
                            try:
                                asyncio.run_coroutine_threadsafe(
                                    ws_send(json.dumps({"type": "agent_output", "data": clean})),
                                    loop
                                )
                            except: pass
        except: pass
    
    def write(self, text):
        if self.process and self.process.stdin:
            self.process.stdin.write(text + "\n")
            self.process.stdin.flush()
    
    def stop(self):
        if self.process:
            self.process.terminate()

# --- Window Tracker ---
def get_running_windows():
    """Get list of visible windows with icons (excludes Python processes)"""
    try:
        import win32gui
        import win32process
        import win32con
        import psutil
        from PIL import Image
        import win32ui
    except ImportError:
        return []
    
    windows = []
    
    def callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return True
        title = win32gui.GetWindowText(hwnd)
        if not title or title in ['', 'Program Manager', 'Windows Input Experience', 'Settings']:
            return True
        if 'Horizon' in title or 'Python' in title:
            return True
        
        # Get process info
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            proc = psutil.Process(pid)
            exe_path = proc.exe()
            exe_name = proc.name().lower()
            
            # Skip python processes
            if 'python' in exe_name:
                return True
            
            # Get icon as base64
            icon_b64 = _extract_icon_b64(exe_path, hwnd)
            
            windows.append({
                "hwnd": hwnd,
                "title": title[:40],
                "exe": exe_path,
                "icon": icon_b64
            })
        except: pass
        return True
    
    try:
        win32gui.EnumWindows(callback, None)
    except: pass
    
    return windows[:12]

def _extract_icon_b64(exe_path, hwnd=None):
    """Extract app icon and return as base64 PNG"""
    try:
        import win32gui
        import win32ui
        import win32con
        from PIL import Image
        
        size = 32
        large, small = win32gui.ExtractIconEx(exe_path, 0, 10)
        if large:
            hicon = large[0]
            hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
            hbmp = win32ui.CreateBitmap()
            hbmp.CreateCompatibleBitmap(hdc, size, size)
            hdc_mem = hdc.CreateCompatibleDC()
            hdc_mem.SelectObject(hbmp)
            hdc_mem.FillSolidRect((0, 0, size, size), 0x000000)
            win32gui.DrawIconEx(hdc_mem.GetSafeHdc(), 0, 0, hicon, size, size, 0, None, win32con.DI_NORMAL)
            bmpstr = hbmp.GetBitmapBits(True)
            img = Image.frombuffer('RGBA', (size, size), bmpstr, 'raw', 'BGRA', 0, 1)
            hdc_mem.DeleteDC()
            win32gui.ReleaseDC(0, hdc.GetSafeHdc())
            for h in large: win32gui.DestroyIcon(h)
            for h in small: win32gui.DestroyIcon(h)
            
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            return base64.b64encode(buf.getvalue()).decode('utf-8')
    except: pass
    return None

def close_window(hwnd):
    """Close a window by hwnd"""
    try:
        import win32gui
        import win32con
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        return True
    except:
        return False

def activate_window(hwnd):
    """Bring window to front"""
    try:
        import win32gui
        import win32con
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        return True
    except:
        return False

# --- Config ---
def load_config():
    try:
        if CONFIG_FILE.exists():
            return json.loads(CONFIG_FILE.read_text())
    except: pass
    return {}

def save_config(data):
    HORIZON_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2))

# --- App ---
agent = AgentProcess()
loop = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global loop
    loop = asyncio.get_event_loop()
    agent.start()
    yield
    agent.stop()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REST Endpoints ---
@app.get("/api/config")
async def get_config():
    return JSONResponse(load_config())

@app.post("/api/config")
async def set_config(data: dict):
    config = load_config()
    config.update(data)
    save_config(config)
    return {"ok": True}

@app.get("/api/windows")
async def get_windows():
    return JSONResponse(get_running_windows())

@app.post("/api/windows/close")
async def post_close_window(data: dict):
    hwnd = data.get("hwnd")
    if hwnd:
        return {"ok": close_window(int(hwnd))}
    return {"ok": False}

@app.post("/api/windows/activate")
async def post_activate_window(data: dict):
    hwnd = data.get("hwnd")
    if hwnd:
        return {"ok": activate_window(int(hwnd))}
    return {"ok": False}

@app.get("/api/wallpapers")
async def get_wallpapers():
    items = []
    if WALLPAPER_DIR.exists():
        for f in WALLPAPER_DIR.iterdir():
            if f.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                items.append({"name": f.name, "path": str(f)})
    return JSONResponse(items)

@app.get("/api/wallpaper-image/{name}")
async def get_wallpaper_image(name: str):
    path = WALLPAPER_DIR / name
    if path.exists():
        return FileResponse(str(path))
    return JSONResponse({"error": "not found"}, status_code=404)

@app.get("/api/fonts")
async def get_fonts():
    """Get system fonts"""
    import tkinter as tk
    from tkinter import font as tkfont
    root = tk.Tk()
    root.withdraw()
    fonts = sorted([f for f in tkfont.families() if not f.startswith("@")])
    root.destroy()
    return JSONResponse(fonts)

@app.post("/api/theme/apply")
async def apply_theme(data: dict):
    wallpaper = data.get("wallpaper")
    if wallpaper:
        try:
            import theme_manager
            tm = theme_manager.ThemeManager()
            tm.apply_theme(wallpaper)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    return {"ok": False}

# --- WebSocket ---
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    agent.ws_clients.append(ws.send_text)
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "query":
                agent.write(msg["data"])
    except WebSocketDisconnect:
        agent.ws_clients.remove(ws.send_text)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=15900, log_level="warning")
