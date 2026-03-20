import React, { useState, useEffect, useCallback, useRef } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { Info, ArrowUp, ArrowDown, ChevronRight, Activity } from 'lucide-react';

const COLORS = {
    primary: 'var(--accent, #10b981)',
    primaryLight: '#34d399',
    secondary: '#3b82f6',
    secondaryLight: '#93c5fd',
    bg: 'var(--border-subtle)',
    text: 'var(--text-main)',
    textSec: 'var(--text-secondary)'
};

const MAX_HISTORY = 40;

const Card = ({ children, style }) => (
    <div style={{
        background: 'var(--bg-panel)',
        borderRadius: '12px',
        border: '1px solid var(--border-subtle)',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 2px 8px rgba(0,0,0,0.02)',
        ...style
    }}>
        {children}
    </div>
);

const CardHeader = ({ title, showInfo = false, action }) => (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '15px' }}>
        <h3 style={{ margin: 0, fontSize: '15px', fontWeight: 600, color: COLORS.text }}>{title}</h3>
        {showInfo && <Info size={16} color={COLORS.textSec} />}
        {action && action}
    </div>
);

const ProgressBar = ({ percent, color = COLORS.primary }) => (
    <div style={{ width: '100%', height: '8px', background: COLORS.bg, borderRadius: '4px', overflow: 'hidden' }}>
        <div style={{ width: `${Math.min(percent, 100)}%`, height: '100%', background: color, borderRadius: '4px', transition: 'width 0.5s ease' }} />
    </div>
);

const Monitor = () => {
    const [history, setHistory] = useState([]);
    const [latest, setLatest] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const intervalRef = useRef(null);

    const fetchMetrics = useCallback(async () => {
        try {
            if (window.pywebview && window.pywebview.api && window.pywebview.api.get_system_metrics) {
                const data = await window.pywebview.api.get_system_metrics();
                if (data && data.success) {
                    setLatest(data);
                    setHistory(prev => {
                        const newPoint = {
                            time: data.time,
                            cpu: data.cpu.percent,
                            ramUsed: data.ram.used_gb,
                            ramCached: data.ram.cached_gb,
                            diskRead: data.disk.read_mb,
                            diskWrite: data.disk.write_mb,
                            netUp: data.net.up_mbps,
                            netDown: data.net.down_mbps,
                        };
                        const next = [...prev, newPoint];
                        return next.length > MAX_HISTORY ? next.slice(next.length - MAX_HISTORY) : next;
                    });
                    setLoading(false);
                    setError(null);
                } else if (data && !data.success) {
                    setError(data.error);
                }
            } else {
                setError("pywebview not available — run via python main_gui.py");
                setLoading(false);
            }
        } catch (e) {
            setError(e.message);
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchMetrics();
        intervalRef.current = setInterval(fetchMetrics, 1500);
        return () => clearInterval(intervalRef.current);
    }, [fetchMetrics]);

    if (loading) {
        return (
            <div style={{ padding: '40px', textAlign: 'center', color: COLORS.textSec }}>
                <Activity size={32} style={{ marginBottom: '12px', opacity: 0.5 }} />
                <div style={{ fontSize: '16px' }}>Loading real system metrics...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ padding: '40px', textAlign: 'center', color: '#ef4444' }}>
                <div style={{ fontSize: '16px' }}>⚠️ {error}</div>
            </div>
        );
    }

    const cpu = latest?.cpu ?? {};
    const ram = latest?.ram ?? {};
    const disk = latest?.disk ?? {};
    const net = latest?.net ?? {};
    const barData = history.slice(-10);

    return (
        <div style={{ padding: '0px 20px 40px 20px', maxWidth: '1400px', margin: '0 auto' }}>
            <h1 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '24px', color: COLORS.text }}>
                System Monitor
                <span style={{ fontSize: '12px', fontWeight: 400, color: COLORS.textSec, marginLeft: '12px' }}>
                    Live — updates every 1.5s
                </span>
            </h1>

            {/* TOP 4 SUMMARY CARDS */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px', marginBottom: '20px' }}>

                {/* CPU Card */}
                <Card style={{ position: 'relative', overflow: 'hidden' }}>
                    <CardHeader title="CPU Usage" showInfo />
                    <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginTop: '10px' }}>
                        <div>
                            <div style={{ fontSize: '32px', fontWeight: 700, lineHeight: 1 }}>
                                {cpu.percent}<span style={{ fontSize: '18px' }}>%</span>
                            </div>
                        </div>
                        <div style={{ fontSize: '12px', color: COLORS.textSec, textAlign: 'right' }}>
                            <div>{cpu.cores} Cores</div>
                            <div>{cpu.freq_mhz} MHz</div>
                        </div>
                    </div>
                    <div style={{ position: 'absolute', bottom: '-20px', right: '10px', width: '120px', height: '60px', minWidth: '1px', minHeight: '1px' }}>
                        <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
                            <PieChart>
                                <Pie data={[{ value: cpu.percent }, { value: 100 - cpu.percent }]} cx="50%" cy="100%" startAngle={180} endAngle={0} innerRadius={40} outerRadius={50} dataKey="value" stroke="none">
                                    <Cell fill={COLORS.primary} />
                                    <Cell fill={COLORS.bg} />
                                </Pie>
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </Card>

                {/* RAM Card */}
                <Card>
                    <CardHeader title="RAM Usage" showInfo />
                    <div style={{ marginTop: 'auto' }}>
                        <div style={{ fontSize: '32px', fontWeight: 700, marginBottom: '10px' }}>
                            {ram.used_gb} <span style={{ fontSize: '18px', fontWeight: 500 }}>GB</span>
                        </div>
                        <ProgressBar percent={ram.percent} />
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', fontSize: '13px', color: COLORS.textSec }}>
                            <span>Total: {ram.total_gb} GB</span>
                            <span style={{ fontWeight: 600, color: COLORS.text }}>{ram.percent}%</span>
                        </div>
                    </div>
                </Card>

                {/* Disk Card */}
                <Card>
                    <CardHeader title="Disk Usage" showInfo />
                    <div style={{ marginTop: 'auto' }}>
                        <div style={{ fontSize: '32px', fontWeight: 700, marginBottom: '10px' }}>
                            {disk.percent}<span style={{ fontSize: '18px', fontWeight: 500 }}>%</span>
                        </div>
                        <ProgressBar percent={disk.percent} color="#1e3c72" />
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', fontSize: '13px', color: COLORS.textSec }}>
                            <span>Free: {disk.free_gb} GB</span>
                            <span>{disk.used_gb} / {disk.total_gb} GB</span>
                        </div>
                    </div>
                </Card>

                {/* Network Card */}
                <Card>
                    <CardHeader title="Network Traffic" showInfo />
                    <div style={{ marginTop: 'auto' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '15px' }}>
                            <div style={{ fontSize: '32px', fontWeight: 700 }}>{net.total_mbps} <span style={{ fontSize: '18px', fontWeight: 500 }}>Mbps</span></div>
                        </div>
                        <div style={{ display: 'flex', gap: '20px', fontSize: '13px' }}>
                            <div style={{ color: COLORS.primary, display: 'flex', alignItems: 'center', gap: '4px' }}>
                                <ArrowUp size={16} /> {net.up_mbps} Mbps
                            </div>
                            <div style={{ color: COLORS.secondary, display: 'flex', alignItems: 'center', gap: '4px' }}>
                                <ArrowDown size={16} /> {net.down_mbps} Mbps
                            </div>
                        </div>
                    </div>
                </Card>

            </div>

            {/* BOTTOM 4 CHARTS */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: '20px' }}>

                {/* CPU Chart */}
                <Card style={{ padding: '0', overflow: 'hidden' }}>
                    <div style={{ padding: '20px 20px 0 20px' }}>
                        <CardHeader title="CPU Usage (Live)" />
                    </div>
                    <div style={{ height: '220px', width: '100%', marginTop: '10px', minWidth: '1px', minHeight: '1px' }}>
                        <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
                            <AreaChart data={history} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="cpuColor" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.3} />
                                        <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: COLORS.textSec }} dy={10} minTickGap={40} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: COLORS.textSec }} tickFormatter={(v) => `${v}%`} domain={[0, 100]} />
                                <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid var(--border-subtle)', background: 'var(--bg-panel)' }} formatter={(v) => [`${v}%`, 'CPU']} />
                                <Area type="monotone" dataKey="cpu" stroke={COLORS.primary} strokeWidth={2} fillOpacity={1} fill="url(#cpuColor)" isAnimationActive={false} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '15px 30px', borderTop: '1px solid var(--border-subtle)', background: 'var(--bg-app)', fontSize: '13px' }}>
                        <span>Cores: <strong>{cpu.cores}</strong></span>
                        <span>Freq: <strong>{cpu.freq_mhz} MHz</strong></span>
                        <span>Now: <strong>{cpu.percent}%</strong></span>
                    </div>
                </Card>

                {/* Memory Chart */}
                <Card style={{ padding: '0', overflow: 'hidden' }}>
                    <div style={{ padding: '20px 20px 0 20px' }}>
                        <CardHeader title="Memory Usage (Live)" />
                        <div style={{ fontSize: '28px', fontWeight: 700, marginTop: '5px' }}>{ram.used_gb} GB</div>
                    </div>
                    <div style={{ height: '185px', width: '100%', marginTop: '10px', minWidth: '1px', minHeight: '1px' }}>
                        <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
                            <AreaChart data={history} margin={{ top: 10, right: 0, left: 0, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="ram1" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.5} />
                                        <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0.1} />
                                    </linearGradient>
                                    <linearGradient id="ram2" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor={COLORS.primaryLight} stopOpacity={0.6} />
                                        <stop offset="95%" stopColor={COLORS.primaryLight} stopOpacity={0.1} />
                                    </linearGradient>
                                </defs>
                                <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid var(--border-subtle)' }} formatter={(v, name) => [`${v} GB`, name === 'ramUsed' ? 'Used' : 'Cached']} />
                                <Area type="step" dataKey="ramUsed" stackId="1" stroke={COLORS.primary} strokeWidth={2} fill="url(#ram1)" isAnimationActive={false} />
                                <Area type="step" dataKey="ramCached" stackId="1" stroke={COLORS.primaryLight} strokeWidth={2} fill="url(#ram2)" isAnimationActive={false} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '15px 30px', borderTop: '1px solid var(--border-subtle)', background: 'var(--bg-app)', fontSize: '13px' }}>
                        <span>Cached: <strong>{ram.cached_gb} GB</strong></span>
                        <span>Free: <strong>{ram.free_gb} GB</strong></span>
                        <span>Total: <strong>{ram.total_gb} GB</strong></span>
                    </div>
                </Card>

                {/* Disk I/O Chart */}
                <Card style={{ padding: '0', overflow: 'hidden' }}>
                    <div style={{ padding: '20px 20px 0 20px', display: 'flex', justifyContent: 'space-between' }}>
                        <div>
                            <div style={{ fontSize: '15px', fontWeight: 600 }}>Disk I/O (Live)</div>
                            <div style={{ fontSize: '24px', fontWeight: 700, marginTop: '10px' }}>
                                {(disk.read_mb + disk.write_mb).toFixed(1)} <span style={{ fontSize: '14px' }}>MB/s</span>
                            </div>
                            <div style={{ width: '150px', marginTop: '10px' }}>
                                <ProgressBar percent={Math.min((disk.read_mb + disk.write_mb) / 200 * 100, 100)} color={COLORS.primaryLight} />
                            </div>
                        </div>
                        <div style={{ textAlign: 'right', fontSize: '13px' }}>
                            <div style={{ textAlign: 'right' }}><div style={{ color: COLORS.textSec }}>Read</div><strong>{disk.read_mb} MB/s</strong></div>
                            <div style={{ textAlign: 'right', marginTop: '8px' }}><div style={{ color: COLORS.textSec }}>Write</div><strong>{disk.write_mb} MB/s</strong></div>
                        </div>
                    </div>
                    <div style={{ display: 'flex', marginTop: '5px', minWidth: '1px', minHeight: '1px' }}>
                        <div style={{ height: '160px', flex: 2, minWidth: '1px', minHeight: '1px' }}>
                            <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
                                <AreaChart data={history} margin={{ top: 20, right: 0, left: -20, bottom: 0 }}>
                                    <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: COLORS.textSec }} tickFormatter={(v) => v + 'MB'} />
                                    <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: COLORS.textSec }} minTickGap={40} dy={5} />
                                    <Area type="monotone" dataKey="diskRead" stroke={COLORS.primaryLight} strokeWidth={2} fill={COLORS.primaryLight} fillOpacity={0.2} isAnimationActive={false} />
                                    <Area type="monotone" dataKey="diskWrite" stroke={COLORS.primary} strokeWidth={2} fill={COLORS.primary} fillOpacity={0.2} isAnimationActive={false} />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                        <div style={{ height: '140px', flex: 1, paddingRight: '20px', minWidth: '1px', minHeight: '1px' }}>
                            <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
                                <BarChart data={barData} margin={{ top: 20, right: 0, left: 10, bottom: 20 }}>
                                    <Bar dataKey="diskRead" stackId="a" fill={COLORS.primaryLight} radius={[0, 0, 4, 4]} barSize={8} isAnimationActive={false} />
                                    <Bar dataKey="diskWrite" stackId="a" fill={COLORS.primary} radius={[4, 4, 0, 0]} isAnimationActive={false} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '15px 30px', borderTop: '1px solid var(--border-subtle)', background: 'var(--bg-app)', fontSize: '13px', alignItems: 'center' }}>
                        <span>Read: <strong>{disk.read_mb} MB/s</strong></span>
                        <span>Write: <strong>{disk.write_mb} MB/s</strong></span>
                        <span>Used: <strong>{disk.used_gb} / {disk.total_gb} GB</strong></span>
                    </div>
                </Card>

                {/* Network Activity Chart */}
                <Card style={{ padding: '0', overflow: 'hidden' }}>
                    <div style={{ padding: '20px 20px 0 20px' }}>
                        <CardHeader title="Network Activity (Live)" />
                        <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginTop: '5px', flexWrap: 'wrap' }}>
                            <div style={{ fontSize: '28px', fontWeight: 700 }}>{net.total_mbps} Mbps</div>
                            <div style={{ color: COLORS.primary, display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600, fontSize: '16px' }}><ArrowUp size={16} /> {net.up_mbps} Mbps</div>
                            <div style={{ color: COLORS.secondary, display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600, fontSize: '16px' }}><ArrowDown size={16} /> {net.down_mbps} Mbps</div>
                        </div>
                        <div style={{ width: '100%', height: '4px', background: COLORS.bg, borderRadius: '2px', marginTop: '10px', display: 'flex' }}>
                            <div style={{ width: `${net.total_mbps > 0 ? (net.up_mbps / net.total_mbps * 100) : 50}%`, background: COLORS.primary, borderRadius: '2px' }} />
                            <div style={{ flex: 1, background: COLORS.secondary, borderRadius: '2px' }} />
                        </div>
                    </div>
                    <div style={{ height: '185px', width: '100%', marginTop: '10px', minWidth: '1px', minHeight: '1px' }}>
                        <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
                            <AreaChart data={history} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: COLORS.textSec }} tickFormatter={(v) => v + ' M'} />
                                <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: COLORS.textSec }} minTickGap={40} dy={5} />
                                <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid var(--border-subtle)' }} formatter={(v, name) => [`${v} Mbps`, name === 'netUp' ? '↑ Upload' : '↓ Download']} />
                                <Area type="monotone" dataKey="netUp" stroke={COLORS.primary} strokeWidth={2} fill={COLORS.primary} fillOpacity={0.2} isAnimationActive={false} />
                                <Area type="monotone" dataKey="netDown" stroke={COLORS.secondary} strokeWidth={2} fill={COLORS.secondary} fillOpacity={0.2} isAnimationActive={false} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '15px 30px', borderTop: '1px solid var(--border-subtle)', background: 'var(--bg-app)', fontSize: '13px' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><ArrowUp size={14} color={COLORS.primary} /> Upload: <strong>{net.up_mbps} Mbps</strong></span>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><ArrowDown size={14} color={COLORS.secondary} /> Download: <strong>{net.down_mbps} Mbps</strong></span>
                    </div>
                </Card>

            </div>
        </div>
    );
};

export default Monitor;
