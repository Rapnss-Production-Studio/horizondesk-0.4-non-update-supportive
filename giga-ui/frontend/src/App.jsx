import { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import './App.css'

const API = 'http://127.0.0.1:15900'
const WS_URL = 'ws://127.0.0.1:15900/ws'

const params = new URLSearchParams(window.location.search)
const VIEW = params.get('view') || 'taskbar'

/* ══════════════════════════════════════════════════════════════
   TASKBAR — thin top strip panel
   ══════════════════════════════════════════════════════════════ */
function TaskBar() {
  const [time, setTime] = useState('')
  const [date, setDate] = useState('')
  const [windows, setWindows] = useState([])

  useEffect(() => {
    const tick = () => {
      const now = new Date()
      setTime(now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }))
      setDate(now.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: '2-digit' }))
    }
    tick()
    return () => clearInterval(setInterval(tick, 10000))
  }, [])

  useEffect(() => {
    const poll = async () => {
      try {
        const r = await fetch(`${API}/api/windows`)
        if (r.ok) setWindows(await r.json())
      } catch { }
    }
    poll()
    const id = setInterval(poll, 3000)
    return () => clearInterval(id)
  }, [])

  const activate = (hwnd) => {
    fetch(`${API}/api/windows/activate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ hwnd })
    })
  }

  const closeWin = (hwnd, e) => {
    e.stopPropagation()
    fetch(`${API}/api/windows/close`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ hwnd })
    })
  }

  return (
    <div className="taskbar">
      <div className="taskbar__left">
        <span className="taskbar__star">✦</span>
        <span className="taskbar__name">Horizon</span>
      </div>

      <div className="taskbar__center">
        <AnimatePresence>
          {windows.map(w => (
            <motion.div
              key={w.hwnd}
              className="taskbar__app"
              onClick={() => activate(w.hwnd)}
              title={w.title}
              initial={{ opacity: 0, scale: 0.85 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.85 }}
              transition={{ type: 'spring', stiffness: 400, damping: 28 }}
            >
              {w.icon && <img src={`data:image/png;base64,${w.icon}`} className="taskbar__icon" alt="" />}
              <span className="taskbar__appname">
                {w.title.length > 16 ? w.title.slice(0, 16) + '…' : w.title}
              </span>
              <button className="taskbar__x" onClick={(e) => closeWin(w.hwnd, e)}>×</button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      <div className="taskbar__right">
        <span className="taskbar__time">{time}</span>
        <span className="taskbar__sep">·</span>
        <span className="taskbar__date">{date}</span>
      </div>
    </div>
  )
}

/* ══════════════════════════════════════════════════════════════
   PROMPT — floating rounded input bar
   ══════════════════════════════════════════════════════════════ */
function Prompt() {
  const [text, setText] = useState('')
  const wsRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket(WS_URL)
      ws.onclose = () => setTimeout(connect, 2000)
      wsRef.current = ws
    }
    connect()
    return () => wsRef.current?.close()
  }, [])

  const send = () => {
    const q = text.trim()
    if (!q) return
    wsRef.current?.send(JSON.stringify({ type: 'query', data: q }))
    setText('')
    inputRef.current?.focus()
  }

  return (
    <motion.div
      className="prompt"
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 300, damping: 28, delay: 0.1 }}
    >
      <div className="prompt__bar">
        <span className="prompt__icon">✦</span>
        <input
          ref={inputRef}
          className="prompt__input"
          type="text"
          placeholder="Ask anything..."
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          autoFocus
        />
        <motion.button
          className="prompt__send"
          whileHover={{ scale: 1.08 }}
          whileTap={{ scale: 0.92 }}
          onClick={send}
        >→</motion.button>
      </div>
    </motion.div>
  )
}

/* ══════════════════════════════════════════════════════════════
   APP — Route by ?view= param
   ══════════════════════════════════════════════════════════════ */
function App() {
  if (VIEW === 'prompt') return <Prompt />
  return <TaskBar />
}

export default App
