import React, { useState, useEffect, useRef } from 'react';
import { Send, Cpu, User as UserIcon, Loader, Plus, LayoutGrid, X, Pause, Terminal, ArrowUpCircle } from 'lucide-react';

const LogViewer = () => {
    const [open, setOpen] = useState(false);
    const [logs, setLogs] = useState([
        { type: 'info', text: 'Horizon System Initialized' },
        { type: 'command', text: 'Loading core modules...' }
    ]);
    const logEndRef = useRef(null);

    useEffect(() => {
        const handleToggle = () => setOpen(prev => !prev);
        const handleNewLog = (e) => {
            setLogs(prev => [...prev, e.detail]);
            if (!open) {
                // Peek open slightly or notification?
            }
        };
        window.addEventListener('toggle-logs', handleToggle);
        window.addEventListener('new-log', handleNewLog);
        return () => {
            window.removeEventListener('toggle-logs', handleToggle);
            window.removeEventListener('new-log', handleNewLog);
        };
    }, []);

    useEffect(() => {
        if (open) logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs, open]);

    return (
        <div style={{
            position: 'absolute', top: 0, right: 0, bottom: 0,
            width: open ? '350px' : '0',
            backgroundColor: 'rgba(15, 23, 42, 0.95)',
            backdropFilter: 'blur(10px)',
            borderLeft: open ? '1px solid rgba(255,255,255,0.1)' : 'none',
            transition: 'width 0.3s ease',
            zIndex: 100,
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column'
        }}>
            <div style={{ padding: '16px', borderBottom: '1px solid rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'white' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600, fontSize: '13px' }}>
                    <Terminal size={14} color="var(--accent)" /> System Logs
                </div>
                <X size={16} style={{ cursor: 'pointer', opacity: 0.6 }} onClick={() => setOpen(false)} />
            </div>
            <div style={{ flex: 1, overflowY: 'auto', padding: '12px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {logs.map((log, i) => (
                    <div key={i} style={{ fontSize: '11px', fontFamily: 'monospace', color: log.type === 'command' ? 'var(--accent)' : 'rgba(255,255,255,0.7)', lineBreak: 'anywhere' }}>
                        <span style={{ opacity: 0.4 }}>[{new Date().toLocaleTimeString([], { hour12: false })}]</span> {log.text}
                    </div>
                ))}
                <div ref={logEndRef} />
            </div>
        </div>
    );
};

// --- Media & Markdown Parser ---
// This intelligently parses URLs and file paths to render images/videos inline.
const MessageRenderer = ({ content }) => {
    const renderContent = () => {
        // Updated regex to catch local paths, web URLs, and Markdown image syntax
        const parts = content.split(/(!\[.*?\]\(.*?\)|https?:\/\/[^\s"']+\.(?:mp4|webm|png|jpg|jpeg|gif|webp)|(?:[a-zA-Z]:|[\\/])[^\s"']+\.(?:mp4|webm|png|jpg|jpeg|gif|webp))/gi);

        return parts.map((part, i) => {
            if (!part) return null;

            let src = part;
            let isMarkdown = false;
            let altText = "Agent generated media";

            // Check for Markdown syntax: ![alt](url)
            const mdMatch = part.match(/!\[(.*?)\]\((.*?)\)/);
            if (mdMatch) {
                altText = mdMatch[1] || altText;
                src = mdMatch[2];
                isMarkdown = true;
            }

            const lowerSrc = src.toLowerCase();
            const isVideo = lowerSrc.endsWith('.mp4') || lowerSrc.endsWith('.webm');
            const isImage = lowerSrc.endsWith('.png') || lowerSrc.endsWith('.jpg') || lowerSrc.endsWith('.jpeg') || lowerSrc.endsWith('.gif') || lowerSrc.endsWith('.webp') || isMarkdown;

            if (isVideo || isImage) {
                const finalSrc = src.startsWith('http') ? src : `file:///${src.replace(/\\/g, '/')}`;

                return (
                    <div key={i} style={{ marginTop: '8px', marginBottom: '8px', display: 'block', maxWidth: '100%' }}>
                        <div style={{
                            resize: 'both',
                            overflow: 'hidden',
                            maxWidth: '100%',
                            minWidth: '200px',
                            minHeight: '150px',
                            border: '1px solid var(--border-subtle)',
                            borderRadius: '8px',
                            backgroundColor: 'rgba(0,0,0,0.05)',
                            display: 'flex',
                            position: 'relative'
                        }}>
                            {isVideo ? (
                                <video
                                    src={finalSrc}
                                    controls
                                    style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                                    title={altText}
                                />
                            ) : (
                                <img
                                    src={finalSrc}
                                    alt={altText}
                                    style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                                    title={altText}
                                    onError={(e) => { e.target.style.display = 'none'; }}
                                />
                            )}
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px', wordBreak: 'break-all', opacity: 0.7 }}>
                            {altText !== "Agent generated media" ? altText : (src.length > 50 ? src.substring(0, 50) + "..." : src)}
                        </div>
                    </div>
                );
            }
            return <span key={i}>{part}</span>;
        });
    };

    return (
        <div style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', lineHeight: '1.5' }}>
            {renderContent()}
        </div>
    );
};


const AgentPane = ({ paneId, title, isActive }) => {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([
        { role: 'agent', content: `Hello! I am Horizon Agent [${title}]. How can I help you today?` }
    ]);
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const textareaRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        if (isActive) scrollToBottom();
    }, [messages, isActive]);

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
        }
    }, [input]);

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            if (window.pywebview?.api) {
                const response = await window.pywebview.api.run_agent_prompt(paneId, userMsg.content);
                const agentMsg = { role: 'agent', content: response };
                setMessages(prev => [...prev, agentMsg]);
            } else {
                setTimeout(() => {
                    setMessages(prev => [...prev, { role: 'agent', content: "[Demo Mode]" }]);
                    setLoading(false);
                }, 1000);
            }
        } catch (error) {
            console.error(`Error:`, error);
            setMessages(prev => [...prev, { role: 'agent', content: "Error: " + error }]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div style={{
            display: isActive ? 'flex' : 'none',
            flexDirection: 'column',
            height: '100%',
            backgroundColor: 'var(--bg-app)',
            flex: 1,
            position: 'relative'
        }}>
            {/* Scrollable Chat Area */}
            <div style={{
                flex: 1, overflowY: 'auto', paddingBottom: '160px',
                display: 'flex', flexDirection: 'column', alignItems: 'center'
            }}>
                <div style={{ width: '100%', maxWidth: '800px', display: 'flex', flexDirection: 'column' }}>

                    {/* Welcome Screen (if only 1 message) */}
                    {messages.length === 1 && (
                        <div style={{ height: '30vh', display: 'flex', alignItems: 'flex-end', justifyContent: 'center', marginBottom: '40px' }}>
                            <h1 style={{ fontSize: '2rem', color: 'var(--text-main)', opacity: 0.8, fontWeight: 600 }}>What can I help with?</h1>
                        </div>
                    )}

                    {messages.map((msg, idx) => {
                        // Determine if it's the welcome message to hide its bubble formatting
                        if (msg.role === 'agent' && idx === 0 && messages.length === 1) return null;

                        const isUser = msg.role === 'user';
                        return (
                            <div key={idx} style={{
                                width: '100%',
                                padding: '24px 20px',
                                display: 'flex',
                                justifyContent: 'center',
                                backgroundColor: isUser ? 'transparent' : 'var(--bg-panel)',
                                borderBottom: isUser ? 'none' : '1px solid var(--border-subtle)',
                            }}>
                                <div style={{
                                    width: '100%', maxWidth: '760px', display: 'flex', gap: '20px',
                                    flexDirection: isUser ? 'row-reverse' : 'row'
                                }}>
                                    {/* Avatar */}
                                    <div style={{
                                        width: '30px', height: '30px', borderRadius: '4px',
                                        backgroundColor: isUser ? 'var(--accent)' : '#10a37f', // ChatGPT style green for agent
                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        color: 'white', flexShrink: 0, marginTop: '2px'
                                    }}>
                                        {isUser ? <UserIcon size={18} /> : <Cpu size={18} />}
                                    </div>

                                    {/* Content */}
                                    <div style={{
                                        flex: 1,
                                        color: 'var(--text-main)',
                                        fontSize: '15px',
                                        lineHeight: '1.6',
                                        padding: isUser ? '8px 16px' : '4px 0',
                                        backgroundColor: isUser ? 'var(--bg-panel)' : 'transparent',
                                        borderRadius: isUser ? '16px' : '0',
                                        maxWidth: isUser ? '75%' : '100%',
                                        marginLeft: isUser ? 'auto' : '0',
                                    }}>
                                        {isUser ? msg.content : <MessageRenderer content={msg.content} />}
                                    </div>
                                </div>
                            </div>
                        );
                    })}

                    {loading && (
                        <div style={{ width: '100%', padding: '24px 20px', display: 'flex', justifyContent: 'center' }}>
                            <div style={{ width: '100%', maxWidth: '760px', display: 'flex', gap: '20px' }}>
                                <div style={{
                                    width: '30px', height: '30px', borderRadius: '4px',
                                    backgroundColor: '#10a37f', display: 'flex', alignItems: 'center',
                                    justifyContent: 'center', flexShrink: 0, marginTop: '2px'
                                }}>
                                    <div className="typing-indicator">
                                        <span></span><span></span><span></span>
                                    </div>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', fontSize: '14px', color: 'var(--text-secondary)' }}>
                                    Horizon is thinking...
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} style={{ height: '40px' }} />
                </div>
            </div>

            {/* Input Area (Anchored to bottom, floating above content) */}
            <div style={{
                position: 'absolute', bottom: 0, left: 0, right: 0,
                background: 'linear-gradient(180deg, transparent, var(--bg-app) 20%)',
                padding: '30px 20px 20px 20px', display: 'flex', flexDirection: 'column', alignItems: 'center'
            }}>
                <div style={{
                    width: '100%', maxWidth: '760px', position: 'relative',
                    backgroundColor: 'var(--bg-panel)',
                    borderRadius: '24px',
                    boxShadow: '0 0 15px rgba(0,0,0,0.1)',
                    border: '1px solid var(--border-subtle)',
                    padding: '4px 8px 4px 16px'
                }}>
                    <div style={{ display: 'flex', alignItems: 'flex-end', gap: '10px' }}>
                        <textarea
                            ref={textareaRef}
                            value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={handleKeyDown}
                            placeholder={loading ? "Computing..." : "Message Horizon..."}
                            rows={1}
                            disabled={loading}
                            style={{
                                flex: 1, padding: '12px 0', border: 'none', background: 'transparent',
                                color: 'var(--text-main)', resize: 'none', fontSize: '15px', lineHeight: '1.5',
                                maxHeight: '200px', outline: 'none'
                            }}
                        />
                        {loading ? (
                            <button
                                onClick={() => { if(window.pywebview?.api) window.pywebview.api.stop_agent(paneId); setLoading(false); }}
                                style={{
                                    backgroundColor: '#ef4444',
                                    color: 'white',
                                    border: 'none', borderRadius: '50%',
                                    width: '32px', height: '32px', marginBottom: '8px',
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                }}
                                title="Stop Task"
                            >
                                <Pause size={15} />
                            </button>
                        ) : (
                            <button
                                onClick={handleSend} disabled={loading || !input.trim()}
                                style={{
                                    backgroundColor: (loading || !input.trim()) ? 'var(--bg-selected)' : 'var(--accent)',
                                    color: (loading || !input.trim()) ? 'var(--text-secondary)' : 'white',
                                    border: 'none', borderRadius: '50%',
                                    width: '32px', height: '32px', marginBottom: '8px',
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    cursor: (loading || !input.trim()) ? 'default' : 'pointer',
                                    transition: 'all 0.2s'
                                }}
                            >
                                <Send size={15} style={{ marginLeft: '1px' }} />
                            </button>
                        )}
                    </div>
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '10px', textAlign: 'center' }}>
                    Horizon Agent can make mistakes. Consider verifying important information.
                </div>
            </div>

            {/* Background Logs (Slide-out panel) */}
            <LogViewer />

            <style>{`
                .typing-indicator {
                  display: flex;
                  align-items: center;
                  gap: 4px;
                }
                .typing-indicator span {
                  width: 6px;
                  height: 6px;
                  background-color: var(--accent);
                  border-radius: 50%;
                  display: inline-block;
                  animation: pulse 1.5s infinite ease-in-out;
                }
                .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
                .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
                
                @keyframes pulse {
                  0%, 100% { transform: scale(0.8); opacity: 0.5; }
                  50% { transform: scale(1.2); opacity: 1; }
                }
            `}</style>
        </div>
    );
};


const Home = () => {
    // Tab Management
    const [showUpdatePopup, setShowUpdatePopup] = useState(false);
    const [updateInfo, setUpdateInfo] = useState(null);

    // --- AUTOMATIC UPDATE CHECK ---
    useEffect(() => {
        const checkUpdates = async () => {
            if (window.pywebview?.api?.check_for_updates) {
                try {
                    const res = await window.pywebview.api.check_for_updates();
                    if (res && res.updateAvailable) {
                        setUpdateInfo(res);
                        setShowUpdatePopup(true);
                    }
                } catch (e) {
                    console.error("Update check failed:", e);
                }
            }
        };
        // Delay slightly for smooth transition
        const timer = setTimeout(checkUpdates, 3000);
        return () => clearTimeout(timer);
    }, []);

    const [downloading, setDownloading] = useState(false);
    const [downloadComplete, setDownloadComplete] = useState(false);
    const [installing, setInstalling] = useState(false);
    const [installComplete, setInstallComplete] = useState(false);
    const [localZipPath, setLocalZipPath] = useState(null);
    const [downloadedFile, setDownloadedFile] = useState("");

    const handleDownload = async () => {
        if (!updateInfo?.download_url) return;
        setDownloading(true);
        try {
            const res = await window.pywebview.api.download_update_stage(updateInfo.download_url);
            if (res && res.success) {
                setLocalZipPath(res.local_path);
                setDownloadedFile(res.filename);
                setDownloadComplete(true);
            } else {
                alert("Download failed: " + (res?.error || "Unknown error"));
            }
        } catch (e) {
            alert("Error during download: " + e.message);
        } finally {
            setDownloading(false);
        }
    };

    const handleStartInstallation = async () => {
        if (!localZipPath) return;
        setInstalling(true);
        try {
            // Trigger updater.py (detached)
            const res = await window.pywebview.api.start_installation(localZipPath, updateInfo.latest);
            if (res && res.success) {
                // Artificial delay to simulate installation progress
                setTimeout(() => {
                    setInstalling(false);
                    setInstallComplete(true);
                }, 3000);
            } else {
                alert("Installation failed to start: " + (res?.error || "Unknown error"));
                setInstalling(false);
            }
        } catch (e) {
            alert("Error starting installation: " + e.message);
            setInstalling(false);
        }
    };

    const handleRestart = async () => {
        try {
            await window.pywebview.api.apply_update_now();
        } catch (e) {
            alert("Failed to restart: " + e.message);
        }
    };
    const [workspaces, setWorkspaces] = useState([
        { id: 'agent_1', name: 'Workspace 1' }
    ]);
    const [activeId, setActiveId] = useState('agent_1');

    const addWorkspace = () => {
        if (workspaces.length >= 6) return; // limit to 6 tabs to prevent clutter
        const newId = `agent_${Date.now()}`;
        const newWs = { id: newId, name: `Workspace ${workspaces.length + 1}` };
        setWorkspaces([...workspaces, newWs]);
        setActiveId(newId);
    };

    const removeWorkspace = (idToRemove, e) => {
        e.stopPropagation(); // prevent clicking the tab
        if (workspaces.length === 1) return; // don't close the last one

        const newWorkspaces = workspaces.filter(w => w.id !== idToRemove);
        setWorkspaces(newWorkspaces);

        // If we closed the active tab, switch to the first available one
        if (activeId === idToRemove) {
            setActiveId(newWorkspaces[0].id);
        }
    };

    return (
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--bg-app)' }}>

            {/* Top Tab Bar */}
            <div style={{
                display: 'flex', backgroundColor: 'var(--bg-panel)', borderBottom: '1px solid var(--border-subtle)',
                padding: '8px 8px 0 8px', gap: '4px', overflowX: 'auto'
            }}>
                {workspaces.map(ws => {
                    const isActive = ws.id === activeId;
                    return (
                        <div
                            key={ws.id}
                            onClick={() => setActiveId(ws.id)}
                            style={{
                                padding: '10px 16px',
                                display: 'flex', alignItems: 'center', gap: '10px',
                                backgroundColor: isActive ? 'var(--bg-app)' : 'transparent',
                                borderTopLeftRadius: '8px', borderTopRightRadius: '8px',
                                borderTop: `2px solid ${isActive ? 'var(--accent)' : 'transparent'}`,
                                borderLeft: isActive ? '1px solid var(--border-subtle)' : '1px solid transparent',
                                borderRight: isActive ? '1px solid var(--border-subtle)' : '1px solid transparent',
                                borderBottom: isActive ? '1px solid var(--bg-app)' : '1px solid transparent', // blends with app background
                                marginBottom: '-1px', // pull down to overlap bottom border
                                cursor: 'pointer',
                                color: isActive ? 'var(--text-main)' : 'var(--text-secondary)',
                                fontSize: '14px', fontWeight: isActive ? 600 : 400,
                                userSelect: 'none',
                                transition: 'all 0.1s'
                            }}
                        >
                            {ws.name}

                            {workspaces.length > 1 && (
                                <div
                                    onClick={(e) => removeWorkspace(ws.id, e)}
                                    style={{
                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        borderRadius: '50%', padding: '2px', opacity: isActive ? 1 : 0.5
                                    }}
                                    className="tab-close-btn"
                                >
                                    <X size={14} />
                                </div>
                            )}
                        </div>
                    );
                })}

                {workspaces.length < 6 && (
                    <button
                        onClick={addWorkspace}
                        title="New Workspace"
                        style={{
                            padding: '10px 16px', background: 'none', border: 'none', color: 'var(--text-secondary)',
                            cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center'
                        }}
                    >
                        <Plus size={18} />
                    </button>
                )}
            </div>

            {/* Render ALL panes, but only the active one is visible. 
                This keeps the React state (chat history) alive for background panes! */}
            <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
                {workspaces.map(ws => (
                    <AgentPane
                        key={ws.id}
                        paneId={ws.id}
                        title={ws.name}
                        isActive={ws.id === activeId}
                    />
                ))}
            </div>

            <style>{`
                .tab-close-btn:hover {
                    background-color: var(--bg-selected);
                    color: var(--red);
                }
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
                .spin { animation: spin 1s linear infinite; }
            `}</style>
            {/* --- UPDATE POPUP --- */}
            {showUpdatePopup && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(5px)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999
                }}>
                    <div style={{
                        width: '400px', backgroundColor: 'var(--bg-app)', border: '1px solid var(--border-subtle)',
                        borderRadius: '16px', padding: '30px', boxShadow: '0 20px 50px rgba(0,0,0,0.4)',
                        display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center'
                    }}>
                        <div style={{ width: '60px', height: '60px', borderRadius: '50%', backgroundColor: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px' }}>
                            <ArrowUpCircle size={32} color="white" />
                        </div>
                        <h2 style={{ margin: '0 0 10px 0', fontSize: '24px', fontWeight: 800 }}>Update Available</h2>
                        <p style={{ margin: '0 0 20px 0', color: 'var(--text-secondary)', fontSize: '15px' }}>
                            Horizon Desk v{updateInfo?.latest} is here with new features and improvements.
                        </p>
                        
                        {updateInfo?.release_notes && (
                            <div style={{ 
                                width: '100%', backgroundColor: 'var(--bg-panel)', padding: '15px', borderRadius: '10px', 
                                fontSize: '13px', textAlign: 'left', marginBottom: '25px', color: 'var(--text-main)',
                                border: '1px solid var(--border-subtle)', maxHeight: '100px', overflowY: 'auto'
                            }}>
                                <div style={{ fontWeight: 700, marginBottom: '5px', fontSize: '11px', opacity: 0.6 }}>RELEASE NOTES</div>
                                {updateInfo.release_notes}
                            </div>
                        )}

                        <div style={{ display: 'flex', gap: '12px', width: '100%', flexDirection: 'column' }}>
                            {!downloadComplete ? (
                                <div style={{ display: 'flex', gap: '12px' }}>
                                    <button 
                                        onClick={() => setShowUpdatePopup(false)}
                                        disabled={downloading}
                                        style={{ flex: 1, padding: '12px', borderRadius: '10px', border: '1px solid var(--border-subtle)', background: 'transparent', color: 'var(--text-secondary)', fontWeight: 600, cursor: 'pointer' }}>
                                        Not Now
                                    </button>
                                    <button 
                                        onClick={handleDownload}
                                        disabled={downloading}
                                        style={{ flex: 2, padding: '12px', borderRadius: '10px', border: 'none', background: 'var(--accent)', color: 'white', fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)' }}>
                                        {downloading ? 'Downloading...' : 'Download Update'}
                                    </button>
                                </div>
                            ) : !installComplete ? (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '5px' }}>
                                        Saved: <code style={{ background: 'var(--bg-panel)', padding: '2px 4px', borderRadius: '4px' }}>{downloadedFile}</code>
                                    </div>
                                    <button 
                                        onClick={handleStartInstallation}
                                        disabled={installing}
                                        style={{ width: '100%', padding: '12px', borderRadius: '10px', border: 'none', background: 'var(--accent)', color: 'white', fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)' }}>
                                        {installing ? 'Installing Files...' : 'Start Updating'}
                                    </button>
                                </div>
                            ) : (
                                <button 
                                    onClick={handleRestart}
                                    style={{ width: '100%', padding: '12px', borderRadius: '10px', border: 'none', background: '#3b82f6', color: 'white', fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)' }}>
                                    Restart to Apply
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Home;
