import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Package, Search, Edit3, Trash2, X, Check, Filter } from 'lucide-react';
import { Link } from 'react-router-dom';

const STATUS_OPTIONS = ['all', 'published', 'review', 'draft'];

export default function AllPlugins() {
    const { developerInfo, user, refreshDeveloperInfo, API_BASE } = useAuth();
    const [search, setSearch] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [editPlugin, setEditPlugin] = useState(null);
    const [editForm, setEditForm] = useState({});
    const [saving, setSaving] = useState(false);
    const [deleting, setDeleting] = useState(null);
    const [flash, setFlash] = useState('');

    useEffect(() => {
        if (user?.id) refreshDeveloperInfo(user.id);
    }, [user]);

    const plugins = developerInfo?.plugins || [];

    const filtered = plugins.filter(p => {
        const matchesSearch = p.name?.toLowerCase().includes(search.toLowerCase()) ||
            p.description?.toLowerCase().includes(search.toLowerCase());
        const matchesStatus = statusFilter === 'all' || p.status === statusFilter;
        return matchesSearch && matchesStatus;
    });

    const openEdit = (plugin) => {
        setEditPlugin(plugin);
        setEditForm({
            name: plugin.name || '',
            description: plugin.description || '',
            version: plugin.version || '',
            category: plugin.category || 'general'
        });
    };

    const handleSave = async () => {
        if (!editPlugin) return;
        setSaving(true);
        try {
            const res = await fetch(`${API_BASE}/api/dev/plugins/${editPlugin.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(editForm)
            });
            const data = await res.json();
            if (data.success) {
                setFlash('Plugin updated successfully!');
                setEditPlugin(null);
                if (user?.id) refreshDeveloperInfo(user.id);
                setTimeout(() => setFlash(''), 3000);
            }
        } catch (e) {
            console.error('Update failed', e);
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async (pluginId) => {
        if (!confirm('Are you sure you want to delete this plugin? This cannot be undone.')) return;
        setDeleting(pluginId);
        try {
            const res = await fetch(`${API_BASE}/api/dev/plugins/${pluginId}`, { method: 'DELETE' });
            const data = await res.json();
            if (data.success) {
                setFlash('Plugin deleted.');
                if (user?.id) refreshDeveloperInfo(user.id);
                setTimeout(() => setFlash(''), 3000);
            }
        } catch (e) {
            console.error('Delete failed', e);
        } finally {
            setDeleting(null);
        }
    };

    return (
        <div className="animate-fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <div>
                    <h1 style={{ fontSize: '1.75rem', fontWeight: 400 }}>All Plugins</h1>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Manage all your published and in-review plugins</p>
                </div>
                <Link to="/upload" className="btn-primary">+ New plugin</Link>
            </div>

            {flash && <div className="banner-success">{flash}</div>}

            {/* Filters Row */}
            <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
                <div style={{ flex: 1, position: 'relative' }}>
                    <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                    <input className="input-field" placeholder="Search plugins..." value={search}
                        onChange={e => setSearch(e.target.value)} style={{ paddingLeft: '36px' }} />
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Filter size={16} color="var(--text-muted)" />
                    {STATUS_OPTIONS.map(s => (
                        <button key={s} onClick={() => setStatusFilter(s)}
                            className={statusFilter === s ? 'btn-primary' : 'btn-secondary'}
                            style={{ fontSize: '0.8rem', padding: '6px 12px', textTransform: 'capitalize' }}>
                            {s}
                        </button>
                    ))}
                </div>
            </div>

            {/* Table */}
            <div className="glass-panel" style={{ padding: 0, overflow: 'hidden' }}>
                {filtered.length === 0 ? (
                    <div style={{ padding: '64px 24px', textAlign: 'center' }}>
                        <Package size={48} color="var(--border)" style={{ marginBottom: '16px' }} />
                        <p style={{ color: 'var(--text-muted)' }}>{search ? 'No matching plugins found.' : 'You haven\'t published any plugins yet.'}</p>
                    </div>
                ) : (
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Plugin</th>
                                <th>Status</th>
                                <th>Version</th>
                                <th>Category</th>
                                <th style={{ textAlign: 'right' }}>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.map(plugin => (
                                <tr key={plugin.id}>
                                    <td>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                            <div className="plugin-icon" style={{
                                                background: 'var(--accent-light)', display: 'flex', alignItems: 'center',
                                                justifyContent: 'center', color: 'var(--accent)', fontWeight: 600, fontSize: '0.85rem'
                                            }}>
                                                {plugin.icon_url ? <img src={plugin.icon_url} alt="" style={{ width: '100%', height: '100%', borderRadius: '8px' }} />
                                                    : plugin.name?.[0]?.toUpperCase() || '?'}
                                            </div>
                                            <div>
                                                <div style={{ fontWeight: 500 }}>{plugin.name}</div>
                                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                    {plugin.description}
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                    <td>
                                        <span className={`badge ${plugin.status === 'published' ? 'success' : 'pending'}`}>
                                            {plugin.status === 'published' ? 'Published' : 'In review'}
                                        </span>
                                    </td>
                                    <td style={{ color: 'var(--text-muted)' }}>v{plugin.version}</td>
                                    <td style={{ color: 'var(--text-muted)', textTransform: 'capitalize' }}>{plugin.category}</td>
                                    <td style={{ textAlign: 'right' }}>
                                        <button className="btn-icon" title="Edit" onClick={() => openEdit(plugin)}>
                                            <Edit3 size={16} />
                                        </button>
                                        <button className="btn-icon danger" title="Delete" onClick={() => handleDelete(plugin.id)}
                                            disabled={deleting === plugin.id}>
                                            <Trash2 size={16} />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* Edit Modal */}
            {editPlugin && (
                <div className="modal-overlay" onClick={() => setEditPlugin(null)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                            <h2 style={{ fontSize: '1.25rem', fontWeight: 500 }}>Edit Plugin</h2>
                            <button onClick={() => setEditPlugin(null)} className="btn-icon"><X size={20} /></button>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            <div>
                                <label className="input-label">Name</label>
                                <input className="input-field" value={editForm.name} onChange={e => setEditForm({ ...editForm, name: e.target.value })} />
                            </div>
                            <div>
                                <label className="input-label">Description</label>
                                <textarea className="input-field" rows={3} value={editForm.description}
                                    onChange={e => setEditForm({ ...editForm, description: e.target.value })} />
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                                <div>
                                    <label className="input-label">Version</label>
                                    <input className="input-field" value={editForm.version}
                                        onChange={e => setEditForm({ ...editForm, version: e.target.value })} />
                                </div>
                                <div>
                                    <label className="input-label">Category</label>
                                    <select className="input-field" value={editForm.category}
                                        onChange={e => setEditForm({ ...editForm, category: e.target.value })}>
                                        {['general', 'developer', 'media', 'productivity', 'ai', 'data', 'automation'].map(c =>
                                            <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
                                        )}
                                    </select>
                                </div>
                            </div>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '24px' }}>
                            <button className="btn-secondary" onClick={() => setEditPlugin(null)}>Cancel</button>
                            <button className="btn-primary" onClick={handleSave} disabled={saving}>
                                <Check size={16} /> {saving ? 'Saving...' : 'Save changes'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
