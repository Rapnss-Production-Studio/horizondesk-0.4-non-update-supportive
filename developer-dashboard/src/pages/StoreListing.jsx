import { useEffect, useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { ShoppingBag, Save, Image, ChevronDown } from 'lucide-react';

const TIGRIS_UPLOADER = 'https://sufy-uploader.api-rapnss.workers.dev/tigris-upload';

async function uploadToTigris(file) {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('filename', file.name);
    const res = await fetch(TIGRIS_UPLOADER, { method: 'POST', body: fd });
    if (!res.ok) throw new Error('Upload failed');
    return (await res.json()).url;
}

const CATEGORIES = ['general', 'developer', 'media', 'productivity', 'ai', 'data', 'automation'];

export default function StoreListing() {
    const { developerInfo, user, refreshDeveloperInfo, API_BASE } = useAuth();
    const [selectedId, setSelectedId] = useState('');
    const [form, setForm] = useState({ name: '', description: '', fullDescription: '', category: 'general' });
    const [iconPreview, setIconPreview] = useState(null);
    const [iconFile, setIconFile] = useState(null);
    const [saving, setSaving] = useState(false);
    const [flash, setFlash] = useState('');
    const iconRef = useRef();

    useEffect(() => { if (user?.id) refreshDeveloperInfo(user.id); }, [user]);

    const plugins = developerInfo?.plugins || [];
    const selected = plugins.find(p => p.id === selectedId);

    useEffect(() => {
        if (selected) {
            setForm({
                name: selected.name || '',
                description: selected.description || '',
                fullDescription: selected.full_description || '',
                category: selected.category || 'general'
            });
            setIconPreview(selected.icon_url || null);
            setIconFile(null);
        }
    }, [selectedId]);

    const handleIconChange = (e) => {
        const f = e.target.files?.[0];
        if (!f) return;
        setIconFile(f);
        setIconPreview(URL.createObjectURL(f));
    };

    const handleSave = async () => {
        if (!selectedId) return;
        setSaving(true);
        try {
            let iconUrl = undefined;
            if (iconFile) {
                iconUrl = await uploadToTigris(iconFile);
            }

            const res = await fetch(`${API_BASE}/api/dev/plugins/${selectedId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...form, iconUrl })
            });
            const data = await res.json();
            if (data.success) {
                setFlash('Store listing saved!');
                if (user?.id) refreshDeveloperInfo(user.id);
                setTimeout(() => setFlash(''), 3000);
            }
        } catch (e) {
            console.error('Save failed', e);
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="animate-fade-in">
            <div style={{ marginBottom: '32px' }}>
                <h1 style={{ fontSize: '1.75rem', fontWeight: 400 }}>Store Listing</h1>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Configure how your plugin appears in the Horizon Store</p>
            </div>

            {flash && <div className="banner-success">{flash}</div>}

            {/* Plugin Selector */}
            <div className="glass-panel" style={{ marginBottom: '24px' }}>
                <label className="input-label">Select plugin to edit</label>
                <div style={{ position: 'relative' }}>
                    <select className="input-field" value={selectedId} onChange={e => setSelectedId(e.target.value)}
                        style={{ appearance: 'none', paddingRight: '32px' }}>
                        <option value="">— Choose a plugin —</option>
                        {plugins.map(p => <option key={p.id} value={p.id}>{p.name} (v{p.version})</option>)}
                    </select>
                    <ChevronDown size={16} style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', color: 'var(--text-muted)' }} />
                </div>
            </div>

            {!selectedId ? (
                <div className="glass-panel" style={{ textAlign: 'center', padding: '64px 24px' }}>
                    <ShoppingBag size={48} color="var(--border)" style={{ marginBottom: '16px' }} />
                    <p style={{ color: 'var(--text-muted)' }}>Select a plugin above to edit its store listing.</p>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: '32px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                        {/* Details */}
                        <div className="glass-panel">
                            <h2 style={{ fontSize: '1.1rem', fontWeight: 500, marginBottom: '20px' }}>Listing Details</h2>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                                <div>
                                    <label className="input-label">Plugin name</label>
                                    <input className="input-field" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} maxLength={60} />
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>{form.name.length}/60</div>
                                </div>
                                <div>
                                    <label className="input-label">Short description</label>
                                    <input className="input-field" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} maxLength={80} />
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>{form.description.length}/80</div>
                                </div>
                                <div>
                                    <label className="input-label">Full description</label>
                                    <textarea className="input-field" rows={6} value={form.fullDescription}
                                        onChange={e => setForm({ ...form, fullDescription: e.target.value })}
                                        placeholder="Detailed description of features, usage instructions..." />
                                </div>
                                <div>
                                    <label className="input-label">Category</label>
                                    <select className="input-field" value={form.category} onChange={e => setForm({ ...form, category: e.target.value })}>
                                        {CATEGORIES.map(c => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
                                    </select>
                                </div>
                            </div>
                        </div>

                        <button className="btn-primary" onClick={handleSave} disabled={saving} style={{ alignSelf: 'flex-start', padding: '10px 24px' }}>
                            <Save size={16} /> {saving ? 'Saving...' : 'Save listing'}
                        </button>
                    </div>

                    {/* Icon Sidebar */}
                    <div className="glass-panel">
                        <h2 style={{ fontSize: '1rem', fontWeight: 500, marginBottom: '16px' }}>Store Icon</h2>
                        <div style={{ width: '100%', aspectRatio: '1', borderRadius: 16, border: '1px solid var(--border)', background: 'var(--bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', marginBottom: '16px' }}>
                            {iconPreview ? <img src={iconPreview} style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : <Image size={48} color="var(--border)" />}
                        </div>
                        <input type="file" ref={iconRef} accept="image/*" onChange={handleIconChange} style={{ display: 'none' }} />
                        <button className="btn-secondary" onClick={() => iconRef.current?.click()} style={{ width: '100%' }}>
                            {iconFile ? 'Change icon' : 'Upload icon'}
                        </button>
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '8px' }}>512×512 PNG or JPG recommended. Max 1MB.</p>
                    </div>
                </div>
            )}
        </div>
    );
}
