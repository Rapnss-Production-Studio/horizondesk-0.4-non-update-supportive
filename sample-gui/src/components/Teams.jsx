
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { UserPlus, Users, RefreshCw, LogOut, Send, Paperclip, Hash, MessageSquare,
         CheckCircle, Circle, Zap, ClipboardList, Bot, Upload, AlertCircle, Play, Pause } from 'lucide-react';

// ── Helpers ─────────────────────────────────────────────────
const timeAgo = (ts) => {
    const s = Math.floor((Date.now() - ts) / 1000);
    if (s < 60) return 'just now';
    if (s < 3600) return `${Math.floor(s / 60)}m ago`;
    return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const roleColor = (role = '') => {
    const colors = ['#7C3AED', '#0EA5E9', '#10B981', '#F59E0B', '#EF4444', '#EC4899'];
    let h = 0;
    for (let i = 0; i < role.length; i++) h = (h * 31 + role.charCodeAt(i)) % colors.length;
    return colors[h];
};

const Avatar = ({ name = '?', size = 32 }) => (
    <div style={{
        width: size, height: size, borderRadius: '50%', flexShrink: 0,
        background: `linear-gradient(135deg, ${roleColor(name)}, ${roleColor(name + '1')})`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        color: 'white', fontWeight: 700, fontSize: size * 0.38
    }}>{name[0]?.toUpperCase() || '?'}</div>
);

const Pill = ({ children, color = 'var(--accent)' }) => (
    <span style={{
        background: color, color: 'white', borderRadius: '4px',
        padding: '1px 8px', fontSize: '10px', fontWeight: 700, marginLeft: '6px'
    }}>{children}</span>
);

// ── Message Bubble ───────────────────────────────────────────
const MessageBubble = ({ msg, isMe }) => (
    <div style={{
        display: 'flex', gap: '10px', alignSelf: isMe ? 'flex-end' : 'flex-start',
        maxWidth: '78%', flexDirection: isMe ? 'row-reverse' : 'row',
        animation: 'fadeIn 0.2s ease'
    }}>
        {!isMe && <Avatar name={msg.sender || msg.role} size={32} />}
        <div>
            {!isMe && (
                <div style={{ fontSize: '11px', color: roleColor(msg.role), fontWeight: 600, marginBottom: '3px', paddingLeft: '2px' }}>
                    {msg.sender} · {msg.role}
                </div>
            )}
            <div style={{
                padding: '10px 14px', borderRadius: isMe ? '16px 4px 16px 16px' : '4px 16px 16px 16px',
                background: isMe ? 'var(--accent)' : 'var(--bg-panel)',
                border: isMe ? 'none' : '1px solid var(--border-subtle)',
                color: isMe ? 'white' : 'var(--text-main)',
                fontSize: '13.5px', lineHeight: '1.5', whiteSpace: 'pre-wrap',
                wordBreak: 'break-word'
            }}>
                {msg.attachmentUrl && (
                    <div style={{ marginBottom: '6px' }}>
                        <a href="#" onClick={() => window.pywebview?.api && window.pywebview.api.open_url?.(msg.attachmentUrl)}
                            style={{ color: isMe ? 'rgba(255,255,255,0.9)' : 'var(--accent)', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <Paperclip size={12} /> {msg.attachmentUrl.split('/').pop()}
                        </a>
                    </div>
                )}
                {msg.text}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-secondary)', marginTop: '3px', textAlign: isMe ? 'right' : 'left', paddingLeft: '2px', paddingRight: '2px' }}>
                {timeAgo(msg.timestamp)}
            </div>
        </div>
    </div>
);

// ── Main Teams Component ─────────────────────────────────────
const Teams = () => {
    const [view, setView] = useState('login');      // 'login' | 'dashboard'
    const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'members' | 'tasks' | 'work'
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // Login form
    const [loginTab, setLoginTab] = useState('join');
    const [role, setRole] = useState('');
    const [nameInput, setNameInput] = useState('');
    const [code, setCode] = useState('');
    const [taskMode, setTaskMode] = useState('manual'); // 'manual' | 'auto'

    // Team data
    const [teamData, setTeamData] = useState(() => {
        const saved = localStorage.getItem('horizon_team_data');
        return saved ? JSON.parse(saved) : null;
    });
    const [members, setMembers] = useState([]);
    const [tasks, setTasks] = useState([]);
    const [myTasks, setMyTasks] = useState([]);

    useEffect(() => {
        if (teamData) {
            setView('dashboard');
            localStorage.setItem('horizon_team_data', JSON.stringify(teamData));
        } else {
            localStorage.removeItem('horizon_team_data');
        }
    }, [teamData]);

    // Chat state
    const [messages, setMessages] = useState([]);
    const [chatInput, setChatInput] = useState('');
    const [sending, setSending] = useState(false);
    const messagesEndRef = useRef(null);
    const pollRef = useRef(null);
    const fileInputRef = useRef(null);

    // Leader: Assign Task UI
    const [assignTo, setAssignTo] = useState('');
    const [assignDesc, setAssignDesc] = useState('');
    const [assignType, setAssignType] = useState('code');
    const [assignLoading, setAssignLoading] = useState(false);
    const [assignSuccess, setAssignSuccess] = useState('');

    // Member: Submit Work UI
    const [submitTaskId, setSubmitTaskId] = useState('');
    const [submitContent, setSubmitContent] = useState('');
    const [submitLoading, setSubmitLoading] = useState(false);
    const [submitSuccess, setSubmitSuccess] = useState('');

    // AI Auto-Work
    const [autoWorking, setAutoWorking] = useState(false);
    const [autoLog, setAutoLog] = useState([]);
    const autoWorkRef = useRef(false);

    const API_BASE = 'https://horizon-online.api-rapnss.workers.dev';
    const scrollBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    useEffect(scrollBottom, [messages]);

    // ── API helpers ────────────────────────────────
    const fetchMessages = useCallback(async (teamCode) => {
        const tc = teamCode || teamData?.code;
        if (!tc) return;
        try {
            const res = await fetch(`${API_BASE}/api/team/${tc}/messages?limit=60`);
            const data = await res.json();
            if (data.messages) setMessages(data.messages);
        } catch (e) { /* silent */ }
    }, [teamData?.code]);

    const fetchStatus = async (teamCode) => {
        const tc = teamCode || teamData?.code;
        if (!tc) return;
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/api/team/${tc}/status`);
            const data = await res.json();
            if (data.leader !== undefined) { setMembers(data.members || []); setTasks(data.tasks || []); }
        } catch (e) { console.error(e); }
        setLoading(false);
    };

    const fetchMyTasks = async () => {
        const td = teamData;
        if (!td?.code || !td?.memberId) return;
        try {
            const res = await fetch(`${API_BASE}/api/team/${td.code}/tasks/${td.memberId}`);
            const data = await res.json();
            if (Array.isArray(data.tasks)) setMyTasks(data.tasks);
        } catch (e) { console.error(e); }
    };

    // Poll messages + my-tasks every 3s
    useEffect(() => {
        if (view === 'dashboard' && teamData?.code) {
            fetchMessages(teamData.code);
            fetchStatus(teamData.code);
            if (!teamData.isLeader) fetchMyTasks();
            pollRef.current = setInterval(() => {
                fetchMessages(teamData.code);
                if (!teamData.isLeader) fetchMyTasks();
            }, 3000);
        }
        return () => clearInterval(pollRef.current);
    }, [view, teamData?.code]);

    // ── Team Actions ───────────────────────────────
    const createTeam = async () => {
        if (!role || !nameInput) return setError('Name and Role are required');
        setLoading(true); setError('');
        try {
            const res = await fetch(`${API_BASE}/api/team/create`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role })
            });
            const data = await res.json();
            if (data.success) {
                const td = { code: data.teamCode, myName: nameInput, myRole: role, isLeader: true, taskMode };
                setTeamData(td);
                setView('dashboard'); setActiveTab('chat');
                fetchStatus(data.teamCode);
                await postMessage(data.teamCode, nameInput, role,
                    `👑 ${nameInput} created the team as "${role}" [Mode: ${taskMode === 'auto' ? '⚡ Auto' : '🖐️ Manual'}]`);
            } else setError(data.error || 'Failed to create team');
        } catch (e) { setError(e.message); }
        setLoading(false);
    };

    const joinTeam = async () => {
        if (!code || !role || !nameInput) return setError('Name, Code and Role are required');
        setLoading(true); setError('');
        try {
            const res = await fetch(`${API_BASE}/api/team/join`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code, role })
            });
            const data = await res.json();
            if (data.success) {
                const td = { code, myName: nameInput, myRole: role, isLeader: false, memberId: data.memberId || data.member_id };
                setTeamData(td);
                setView('dashboard'); setActiveTab('chat');
                fetchStatus(code);
                await postMessage(code, nameInput, role, `👋 ${nameInput} joined as "${role}"`);
            } else setError(data.error || 'Failed to join team');
        } catch (e) { setError(e.message); }
        setLoading(false);
    };

    const leaveTeam = () => {
        autoWorkRef.current = false;
        clearInterval(pollRef.current);
        setTeamData(null); setMembers([]); setTasks([]); setMessages([]);
        setMyTasks([]); setAutoLog([]);
        setView('login'); setRole(''); setCode(''); setNameInput('');
    };

    // ── Chat ───────────────────────────────────────
    const postMessage = async (teamCode, sender, memberRole, text, attachmentUrl = null) => {
        try {
            await fetch(`${API_BASE}/api/team/${teamCode}/messages`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sender, role: memberRole, text, attachmentUrl })
            });
        } catch (e) { console.error('Failed to post message:', e); }
    };

    const sendMessage = async () => {
        if (!chatInput.trim() || sending) return;
        setSending(true);
        const text = chatInput.trim();
        setChatInput('');
        const optimistic = { id: `opt_${Date.now()}`, sender: teamData.myName, role: teamData.myRole, text, timestamp: Date.now() };
        setMessages(prev => [...prev, optimistic]);
        await postMessage(teamData.code, teamData.myName, teamData.myRole, text);
        setSending(false);
    };

    const handleFileAttach = async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;
        const fakeUrl = `file://${file.name}`;
        await postMessage(teamData.code, teamData.myName, teamData.myRole, `📎 Shared: ${file.name}`, fakeUrl);
        setMessages(prev => [...prev, { id: `file_${Date.now()}`, sender: teamData.myName, role: teamData.myRole, text: `📎 Shared: ${file.name}`, attachmentUrl: fakeUrl, timestamp: Date.now() }]);
        e.target.value = '';
    };

    // ── Leader: Assign Task ────────────────────────
    const assignTask = async () => {
        if (!assignTo || !assignDesc) return;
        setAssignLoading(true); setAssignSuccess('');
        try {
            const res = await fetch(`${API_BASE}/api/team/${teamData.code}/tasks`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ memberId: assignTo, description: assignDesc, type: assignType })
            });
            const data = await res.json();
            if (data.success || data.taskId) {
                setAssignSuccess(`✅ Task assigned! ID: ${data.taskId}`);
                setAssignDesc(''); setAssignTo('');
                await postMessage(teamData.code, teamData.myName, teamData.myRole,
                    `📋 Task assigned to ${members.find(m => m.id === assignTo)?.role || 'member'}: "${assignDesc}" [${assignType}]`);
                fetchStatus();
            } else setAssignSuccess(`❌ ${data.error || 'Failed'}`);
        } catch (e) { setAssignSuccess(`❌ ${e.message}`); }
        setAssignLoading(false);
    };

    // Leader: Sync Results ─────────────────────────
    const syncResults = async () => {
        setAssignSuccess('Syncing...');
        try {
            const res = await fetch(`${API_BASE}/api/team/${teamData.code}/results`);
            const data = await res.json();
            const count = data.results?.length || 0;
            setAssignSuccess(`✅ Synced ${count} result(s)`);
        } catch (e) { setAssignSuccess(`❌ ${e.message}`); }
    };

    // ── Member: Submit Work ────────────────────────
    const submitWork = async () => {
        if (!submitTaskId || !submitContent) return;
        setSubmitLoading(true); setSubmitSuccess('');
        try {
            const res = await fetch(`${API_BASE}/api/team/${teamData.code}/results`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ taskId: submitTaskId, memberId: teamData.memberId, filename: `output_${submitTaskId}.txt`, content: submitContent })
            });
            const data = await res.json();
            if (data.success) {
                setSubmitSuccess('✅ Work submitted to leader!');
                setSubmitContent(''); setSubmitTaskId('');
                await postMessage(teamData.code, teamData.myName, teamData.myRole, `✅ Submitted work for task ${submitTaskId}`);
            } else setSubmitSuccess(`❌ ${data.error || 'Failed'}`);
        } catch (e) { setSubmitSuccess(`❌ ${e.message}`); }
        setSubmitLoading(false);
    };

    // ── Member: Auto-Work Mode ─────────────────────
    const toggleAutoWork = async () => {
        if (autoWorking) {
            autoWorkRef.current = false;
            setAutoWorking(false);
            setAutoLog(prev => [...prev, '⏹️ Auto-work stopped.']);
            return;
        }
        autoWorkRef.current = true;
        setAutoWorking(true);
        setAutoLog(['⚡ Auto-work started. Polling for tasks every 10s...']);

        const processedTasks = new Set();

        const poll = async () => {
            while (autoWorkRef.current) {
                setAutoLog(prev => [...prev, `🔍 Checking for new tasks...`]);
                try {
                    const res = await fetch(`${API_BASE}/api/team/${teamData.code}/tasks/${teamData.memberId}`);
                    const data = await res.json();
                    const pendingTasks = (data.tasks || []).filter(t => t.status === 'pending' && !processedTasks.has(t.id));
                    for (const task of pendingTasks) {
                        processedTasks.add(task.id);
                        setAutoLog(prev => [...prev, `📋 New task: "${task.description}"`]);
                        setAutoLog(prev => [...prev, `🤖 Running AI agent...`]);
                        try {
                            if (window.pywebview?.api) {
                                const result = await window.pywebview.api.run_agent_prompt('auto_work', task.description);
                                // Submit result
                                await fetch(`${API_BASE}/api/team/${teamData.code}/results`, {
                                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({ taskId: task.id, memberId: teamData.memberId, filename: `output_${task.id}.txt`, content: result })
                                });
                                setAutoLog(prev => [...prev, `✅ Task done & submitted!`]);
                                await postMessage(teamData.code, teamData.myName, teamData.myRole, `✅ [Auto] Completed task: "${task.description}"`);
                            } else {
                                setAutoLog(prev => [...prev, `⚠️ pywebview not available — cannot run AI`]);
                            }
                        } catch (e) { setAutoLog(prev => [...prev, `❌ Error: ${e.message}`]); }
                    }
                } catch (e) { setAutoLog(prev => [...prev, `❌ Poll error: ${e.message}`]); }
                // Wait 10s
                await new Promise(r => setTimeout(r, 10000));
            }
        };
        poll();
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    };

    // ════ RENDER — LOGIN ═══════════════════════════
    if (view === 'login') return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                <MessageSquare size={40} color="var(--accent)" style={{ marginBottom: '12px' }} />
                <h2 style={{ margin: 0, fontSize: '24px' }}>Horizon Online</h2>
                <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>AI-powered team collaboration</p>
            </div>

            <div className="card" style={{ width: '420px', padding: '32px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'flex', gap: '8px', background: 'var(--bg-app)', borderRadius: '8px', padding: '4px' }}>
                    {['join', 'create'].map(t => (
                        <button key={t} onClick={() => setLoginTab(t)} style={{
                            flex: 1, padding: '9px', borderRadius: '6px', border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: '13px',
                            background: loginTab === t ? 'var(--accent)' : 'transparent',
                            color: loginTab === t ? 'white' : 'var(--text-secondary)', transition: 'all 0.2s'
                        }}>{t === 'join' ? 'Join Team' : 'Create Team'}</button>
                    ))}
                </div>

                <input type="text" placeholder="Your Name (e.g. Aarav)" value={nameInput} onChange={e => setNameInput(e.target.value)}
                    style={{ padding: '11px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--text-main)', fontSize: '14px' }} />
                <input type="text" placeholder="Your Role (e.g. Backend Developer)" value={role} onChange={e => setRole(e.target.value)}
                    style={{ padding: '11px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--text-main)', fontSize: '14px' }} />

                {loginTab === 'join' && (
                    <input type="text" placeholder="Team Code (6 digits)" value={code} onChange={e => setCode(e.target.value)} maxLength={6}
                        style={{ padding: '11px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--text-main)', fontSize: '14px', letterSpacing: '3px', fontWeight: 600 }} />
                )}

                {loginTab === 'create' && (
                    <div>
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px', fontWeight: 600 }}>Task Distribution Mode</div>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            {[['manual', '🖐️ Manual', 'Members review & complete with AI, then submit'], ['auto', '⚡ Auto', 'AI auto-executes and submits all tasks']].map(([val, label, desc]) => (
                                <button key={val} onClick={() => setTaskMode(val)} style={{
                                    flex: 1, padding: '10px 8px', borderRadius: '8px', border: `2px solid ${taskMode === val ? 'var(--accent)' : 'var(--border-subtle)'}`,
                                    background: taskMode === val ? 'rgba(var(--accent-rgb, 16,185,129),0.1)' : 'var(--bg-app)',
                                    color: taskMode === val ? 'var(--accent)' : 'var(--text-secondary)',
                                    cursor: 'pointer', fontSize: '12px', fontWeight: 600, textAlign: 'center'
                                }}>
                                    <div>{label}</div>
                                    <div style={{ fontSize: '10px', fontWeight: 400, marginTop: '2px', opacity: 0.8 }}>{desc}</div>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {error && <div style={{ color: 'var(--red)', fontSize: '13px', textAlign: 'center' }}>{error}</div>}

                <button onClick={loginTab === 'join' ? joinTeam : createTeam} disabled={loading}
                    style={{ padding: '13px', borderRadius: '8px', border: 'none', cursor: loading ? 'default' : 'pointer', background: 'var(--accent)', color: 'white', fontWeight: 700, fontSize: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                    {loading ? 'Processing...' : (loginTab === 'join' ? <><Users size={16} /> Join Team</> : <><UserPlus size={16} /> Create Team</>)}
                </button>
            </div>
        </div>
    );

    // ════ RENDER — DASHBOARD ════════════════════════
    const tabs = teamData?.isLeader
        ? ['chat', 'members', 'tasks', 'assign']
        : ['chat', 'members', 'my-tasks', 'work'];

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* Header */}
            <div style={{
                padding: '12px 20px', borderBottom: '1px solid var(--border-subtle)', background: 'var(--bg-panel)',
                display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Avatar name={teamData?.myName || '?'} size={36} />
                    <div>
                        <div style={{ fontWeight: 700, fontSize: '15px' }}>
                            <Hash size={13} style={{ verticalAlign: 'middle', marginRight: '2px' }} />Team {teamData?.code}
                            {teamData?.isLeader && <Pill>Leader</Pill>}
                            {teamData?.taskMode === 'auto' && teamData?.isLeader && <Pill color="#7C3AED">⚡ Auto Mode</Pill>}
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                            {teamData?.myName} · {teamData?.myRole}
                        </div>
                    </div>
                </div>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                    {tabs.map(t => (
                        <button key={t} onClick={() => { setActiveTab(t); if (t === 'chat') fetchMessages(); else if (t === 'members' || t === 'tasks' || t === 'assign') fetchStatus(); else if (t === 'my-tasks') fetchMyTasks(); }}
                            style={{
                                padding: '6px 12px', borderRadius: '6px', border: 'none', cursor: 'pointer', fontSize: '12px', fontWeight: 600, textTransform: 'capitalize',
                                background: activeTab === t ? 'var(--accent)' : 'var(--bg-app)', color: activeTab === t ? 'white' : 'var(--text-secondary)'
                            }}>
                            {t === 'assign' ? '📋 Assign' : t === 'my-tasks' ? '🗂️ My Tasks' : t === 'work' ? '🤖 Work' : t.charAt(0).toUpperCase() + t.slice(1)}
                        </button>
                    ))}
                    <button onClick={() => { fetchStatus(); fetchMessages(); if (!teamData.isLeader) fetchMyTasks(); }}
                        style={{ padding: '6px 10px', borderRadius: '6px', border: '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                        <RefreshCw size={14} className={loading ? 'spin' : ''} />
                    </button>
                    <button onClick={leaveTeam}
                        style={{ padding: '6px 10px', borderRadius: '6px', border: '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--red)', cursor: 'pointer' }}>
                        <LogOut size={14} />
                    </button>
                </div>
            </div>

            <div style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>

                {/* ── CHAT TAB ── */}
                {activeTab === 'chat' && (
                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
                        <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            {messages.length === 0 && (
                                <div style={{ textAlign: 'center', color: 'var(--text-secondary)', marginTop: '60px' }}>
                                    <MessageSquare size={48} style={{ opacity: 0.2, marginBottom: '12px' }} />
                                    <div style={{ fontSize: '14px' }}>No messages yet. Say hello! 👋</div>
                                </div>
                            )}
                            {messages.map((msg) => (
                                <MessageBubble key={msg.id} msg={msg} isMe={msg.sender === teamData?.myName} />
                            ))}
                            <div ref={messagesEndRef} />
                        </div>
                        <div style={{ padding: '14px 20px', borderTop: '1px solid var(--border-subtle)', background: 'var(--bg-panel)', display: 'flex', gap: '10px', alignItems: 'center', flexShrink: 0 }}>
                            <input type="file" ref={fileInputRef} onChange={handleFileAttach} style={{ display: 'none' }} />
                            <button onClick={() => fileInputRef.current?.click()} title="Attach file"
                                style={{ padding: '9px', borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--text-secondary)', cursor: 'pointer', flexShrink: 0 }}>
                                <Paperclip size={16} />
                            </button>
                            <textarea value={chatInput} onChange={e => setChatInput(e.target.value)} onKeyDown={handleKeyDown}
                                placeholder={`Message #team-${teamData?.code}...`} rows={1}
                                style={{ flex: 1, padding: '10px 14px', borderRadius: '10px', border: '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--text-main)', resize: 'none', fontSize: '14px', lineHeight: '1.4', maxHeight: '140px' }} />
                            <button onClick={sendMessage} disabled={sending || !chatInput.trim()}
                                style={{ padding: '10px 16px', borderRadius: '10px', border: 'none', background: 'var(--accent)', color: 'white', cursor: 'pointer', flexShrink: 0, display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600 }}>
                                <Send size={15} /> {sending ? '...' : 'Send'}
                            </button>
                        </div>
                    </div>
                )}

                {/* ── MEMBERS TAB ── */}
                {activeTab === 'members' && (
                    <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        <h3 style={{ margin: '0 0 10px' }}>Team Members ({members.length})</h3>
                        {members.length === 0 && <p style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>No members yet. Share the team code: <strong>{teamData?.code}</strong></p>}
                        {members.map(m => (
                            <div key={m.id} className="card" style={{ padding: '14px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <Avatar name={m.role} size={40} />
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontWeight: 600 }}>{m.role}</div>
                                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>ID: {m.id?.substring(0, 18)}...</div>
                                    <div style={{ fontSize: '11px', color: 'var(--green)', marginTop: '2px' }}>● {m.status || 'ready'}</div>
                                </div>
                                {teamData?.isLeader && (
                                    <button onClick={() => { setAssignTo(m.id); setActiveTab('assign'); }}
                                        style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--accent)', background: 'transparent', color: 'var(--accent)', cursor: 'pointer', fontSize: '12px', fontWeight: 600 }}>
                                        Assign Task →
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {/* ── TASKS TAB (Leader: all team tasks) ── */}
                {activeTab === 'tasks' && (
                    <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                            <h3 style={{ margin: 0 }}>Team Tasks ({tasks.length})</h3>
                            <button onClick={syncResults} style={{ padding: '7px 14px', borderRadius: '8px', border: 'none', background: 'var(--accent)', color: 'white', cursor: 'pointer', fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
                                <Upload size={14} /> Sync Results
                            </button>
                        </div>
                        {assignSuccess && <div style={{ color: assignSuccess.startsWith('✅') ? 'var(--green)' : 'var(--red)', fontSize: '13px', fontWeight: 600 }}>{assignSuccess}</div>}
                        {tasks.length === 0 && <p style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>No tasks yet. Use the Assign tab to create one.</p>}
                        {tasks.map(t => (
                            <div key={t.id} className="card" style={{ padding: '16px', borderLeft: `4px solid ${t.status === 'completed' ? 'var(--green)' : 'var(--accent)'}` }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                                    {t.status === 'completed' ? <CheckCircle size={16} color="var(--green)" /> : <Circle size={16} color="var(--accent)" />}
                                    <span style={{ fontWeight: 600 }}>{t.description}</span>
                                </div>
                                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'flex', gap: '12px' }}>
                                    <span>Type: {t.type}</span>
                                    <span>Assigned to: {members.find(m => m.id === t.memberId)?.role || t.memberId?.substring(0, 12) || 'unknown'}...</span>
                                    <span style={{ color: t.status === 'completed' ? 'var(--green)' : 'var(--accent)', fontWeight: 700, textTransform: 'uppercase' }}>{t.status}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* ── ASSIGN TAB (Leader) ── */}
                {activeTab === 'assign' && (
                    <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '600px' }}>
                        <h3 style={{ margin: 0 }}>📋 Assign Task to Member</h3>
                        <div>
                            <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '6px' }}>Select Member</label>
                            <select value={assignTo} onChange={e => setAssignTo(e.target.value)}
                                style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--text-main)', fontSize: '14px' }}>
                                <option value="">— Choose member —</option>
                                {members.map(m => <option key={m.id} value={m.id}>{m.role} ({m.id?.substring(0, 12)}...)</option>)}
                            </select>
                            {members.length === 0 && <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>⚠️ No members yet. Refresh to load members who have joined.</div>}
                        </div>
                        <div>
                            <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '6px' }}>Task Description</label>
                            <textarea value={assignDesc} onChange={e => setAssignDesc(e.target.value)} placeholder="Describe what the member (and AI) needs to do..."
                                rows={4} style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--text-main)', fontSize: '14px', resize: 'vertical', boxSizing: 'border-box' }} />
                        </div>
                        <div>
                            <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '6px' }}>Task Type</label>
                            <div style={{ display: 'flex', gap: '8px' }}>
                                {['code', 'design', 'research', 'write'].map(type => (
                                    <button key={type} onClick={() => setAssignType(type)} style={{
                                        padding: '8px 16px', borderRadius: '8px', border: `2px solid ${assignType === type ? 'var(--accent)' : 'var(--border-subtle)'}`,
                                        background: assignType === type ? 'var(--accent)' : 'transparent',
                                        color: assignType === type ? 'white' : 'var(--text-secondary)',
                                        cursor: 'pointer', fontSize: '13px', fontWeight: 600, textTransform: 'capitalize'
                                    }}>{type}</button>
                                ))}
                            </div>
                        </div>
                        {assignSuccess && <div style={{ color: assignSuccess.startsWith('✅') ? 'var(--green)' : 'var(--red)', fontSize: '13px', fontWeight: 600 }}>{assignSuccess}</div>}
                        <button onClick={assignTask} disabled={assignLoading || !assignTo || !assignDesc}
                            style={{ padding: '13px', borderRadius: '8px', border: 'none', cursor: 'pointer', background: 'var(--accent)', color: 'white', fontWeight: 700, fontSize: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                            <ClipboardList size={16} /> {assignLoading ? 'Assigning...' : 'Assign Task'}
                        </button>
                    </div>
                )}

                {/* ── MY TASKS TAB (Member) ── */}
                {activeTab === 'my-tasks' && (
                    <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                            <h3 style={{ margin: 0 }}>🗂️ My Tasks ({myTasks.length})</h3>
                            <button onClick={fetchMyTasks} style={{ padding: '7px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                <RefreshCw size={13} /> Refresh
                            </button>
                        </div>
                        {myTasks.length === 0 && <p style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>No pending tasks assigned to you.</p>}
                        {myTasks.map(t => (
                            <div key={t.id} className="card" style={{ padding: '16px', borderLeft: `4px solid ${t.status === 'completed' ? 'var(--green)' : 'var(--accent)'}` }}>
                                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '12px' }}>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                                            {t.status === 'completed' ? <CheckCircle size={16} color="var(--green)" /> : <Circle size={16} color="var(--accent)" />}
                                            <span style={{ fontWeight: 600 }}>{t.description}</span>
                                        </div>
                                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'flex', gap: '12px' }}>
                                            <span>Type: {t.type}</span>
                                            <span style={{ color: t.status === 'completed' ? 'var(--green)' : 'var(--accent)', fontWeight: 700, textTransform: 'uppercase' }}>{t.status}</span>
                                        </div>
                                        <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>Task ID: {t.id}</div>
                                    </div>
                                    {t.status !== 'completed' && (
                                        <button onClick={() => { setSubmitTaskId(t.id); setActiveTab('work'); }}
                                            style={{ padding: '6px 12px', borderRadius: '6px', border: 'none', background: 'var(--accent)', color: 'white', cursor: 'pointer', fontSize: '12px', fontWeight: 600, flexShrink: 0 }}>
                                            Submit Work →
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* ── WORK TAB (Member: Submit + Auto-Work) ── */}
                {activeTab === 'work' && (
                    <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>

                        {/* Submit Work Section */}
                        <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
                            <h4 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}><Upload size={16} /> Submit Work to Leader</h4>
                            <div>
                                <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '6px' }}>Task ID</label>
                                <input type="text" value={submitTaskId} onChange={e => setSubmitTaskId(e.target.value)} placeholder="Paste task ID from My Tasks"
                                    style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--text-main)', fontSize: '14px', boxSizing: 'border-box' }} />
                            </div>
                            <div>
                                <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '6px' }}>Your Work / Result</label>
                                <textarea value={submitContent} onChange={e => setSubmitContent(e.target.value)} rows={6}
                                    placeholder="Paste your AI output, code, report, or result here..."
                                    style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'var(--bg-app)', color: 'var(--text-main)', fontSize: '13px', resize: 'vertical', boxSizing: 'border-box' }} />
                            </div>
                            {submitSuccess && <div style={{ color: submitSuccess.startsWith('✅') ? 'var(--green)' : 'var(--red)', fontSize: '13px', fontWeight: 600 }}>{submitSuccess}</div>}
                            <button onClick={submitWork} disabled={submitLoading || !submitTaskId || !submitContent}
                                style={{ padding: '12px', borderRadius: '8px', border: 'none', cursor: 'pointer', background: 'var(--accent)', color: 'white', fontWeight: 700, fontSize: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                                <Send size={15} /> {submitLoading ? 'Submitting...' : 'Submit Work'}
                            </button>
                        </div>

                        {/* Auto-Work Section */}
                        <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
                            <h4 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}><Bot size={16} /> Auto-Work Mode</h4>
                            <p style={{ margin: 0, fontSize: '13px', color: 'var(--text-secondary)' }}>
                                Automatically polls for new tasks every 10 seconds, runs the AI agent on each one, and submits results to the leader — no manual input needed.
                            </p>
                            <button onClick={toggleAutoWork}
                                style={{
                                    padding: '13px', borderRadius: '8px', border: 'none', cursor: 'pointer', fontWeight: 700, fontSize: '14px',
                                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
                                    background: autoWorking ? '#ef4444' : '#7C3AED', color: 'white'
                                }}>
                                {autoWorking ? <><Pause size={16} /> Stop Auto-Work</> : <><Play size={16} /> Start Auto-Work</>}
                            </button>
                            {autoLog.length > 0 && (
                                <div style={{ background: 'var(--bg-app)', borderRadius: '8px', padding: '12px', fontFamily: 'monospace', fontSize: '12px', maxHeight: '200px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                                    {autoLog.map((line, i) => <div key={i} style={{ color: line.startsWith('❌') ? '#ef4444' : line.startsWith('✅') ? '#10b981' : 'var(--text-main)' }}>{line}</div>)}
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>

            <style>{`
                @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
                .spin { animation: spin 1s linear infinite; }
            `}</style>
        </div>
    );
};

export default Teams;
