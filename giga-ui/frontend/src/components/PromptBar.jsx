import { useState, useRef } from 'react'

export default function PromptBar({ onSend }) {
    const [text, setText] = useState('')
    const inputRef = useRef(null)

    const handleSend = () => {
        const q = text.trim()
        if (!q) return
        onSend(q)
        setText('')
        inputRef.current?.focus()
    }

    return (
        <div className="prompt-bar">
            <div className="prompt-bar__container">
                <input
                    ref={inputRef}
                    className="prompt-bar__input"
                    type="text"
                    placeholder="Ask Horizon anything..."
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    autoFocus
                />
                <button className="prompt-bar__send" onClick={handleSend}>
                    ↑
                </button>
            </div>
        </div>
    )
}
