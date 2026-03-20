import { useState, useEffect } from 'react'

export default function DockBar({ windows, onCloseWindow, onActivateWindow, onOpenSettings }) {
    const [time, setTime] = useState('')

    useEffect(() => {
        const tick = () => {
            const now = new Date()
            setTime(now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true }))
        }
        tick()
        const id = setInterval(tick, 10000)
        return () => clearInterval(id)
    }, [])

    return (
        <div className="dock-bar">
            <div className="dock-bar__left">
                <span style={{ fontSize: 16 }}>✦</span>
                <span className="dock-bar__title">Horizon</span>
                <div className="dock-bar__apps">
                    {windows.map((w) => (
                        <div
                            key={w.hwnd}
                            className="dock-bar__app"
                            onClick={() => onActivateWindow(w.hwnd)}
                            title={w.title}
                        >
                            {w.icon ? (
                                <img
                                    className="dock-bar__app-icon"
                                    src={`data:image/png;base64,${w.icon}`}
                                    alt=""
                                />
                            ) : (
                                <span style={{ fontSize: 14 }}>□</span>
                            )}
                            <span>{w.title.length > 18 ? w.title.slice(0, 18) + '…' : w.title}</span>
                            <button
                                className="dock-bar__app-close"
                                onClick={(e) => { e.stopPropagation(); onCloseWindow(w.hwnd) }}
                                title="Close"
                            >
                                ✕
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            <div className="dock-bar__right">
                <button className="dock-bar__btn" onClick={onOpenSettings} title="Settings">
                    ⚙
                </button>
                <span className="dock-bar__time">{time}</span>
            </div>
        </div>
    )
}
