export default function ResponsePanel({ text, onClose }) {
    return (
        <div className="response-panel">
            <div className="response-panel__header">
                <span className="response-panel__title">
                    <span className="response-panel__dot" />
                    Horizon
                </span>
                <button className="response-panel__close" onClick={onClose}>✕</button>
            </div>
            <div className="response-panel__body">
                {text || 'Thinking...'}
            </div>
        </div>
    )
}
