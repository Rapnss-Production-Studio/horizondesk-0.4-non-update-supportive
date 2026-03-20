import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { UploadCloud, Image, CheckCircle, ArrowLeft, Info, HelpCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

const TIGRIS_UPLOADER = 'https://sufy-uploader.api-rapnss.workers.dev/tigris-upload';

async function uploadToTigris(file) {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('filename', file.name);
    const res = await fetch(TIGRIS_UPLOADER, { method: 'POST', body: fd });
    if (!res.ok) throw new Error('File upload failed');
    const data = await res.json();
    return data.url;
}

const CATEGORIES = ['general', 'developer', 'media', 'productivity', 'ai', 'data', 'automation'];

export default function UploadPlugin() {
    const navigate = useNavigate();
    const { developerInfo, API_BASE } = useAuth();

    const [name, setName] = useState('');
    const [shortDesc, setShortDesc] = useState('');
    const [fullDesc, setFullDesc] = useState('');
    const [version, setVersion] = useState('1.0.0');
    const [category, setCategory] = useState('general');

    const [pluginFile, setPluginFile] = useState(null);
    const [iconFile, setIconFile] = useState(null);
    const [iconPreview, setIconPreview] = useState(null);

    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const pluginRef = useRef();
    const iconRef = useRef();

    const handleIconChange = (e) => {
        const f = e.target.files?.[0];
        if (!f) return;
        setIconFile(f);
        setIconPreview(URL.createObjectURL(f));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!pluginFile) return setError('Please select a plugin file (.zip only).');
        if (!name || !shortDesc || !version) return setError('Essential fields are required.');
        if (!developerInfo?.id) return setError('Developer account not found. Please log in again.');

        setUploading(true);
        setError('');
        setSuccess('');

        try {
            setSuccess('Uploading plugin archive...');
            const tigrisUrl = await uploadToTigris(pluginFile);

            let iconUrl = null;
            if (iconFile) {
                setSuccess('Uploading store icon...');
                iconUrl = await uploadToTigris(iconFile);
            }

            setSuccess('Creating release...');
            const res = await fetch(`${API_BASE}/api/dev/plugins`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    developerId: developerInfo.id,
                    name, 
                    description: shortDesc, // API currently uses 'description' as main
                    fullDescription: fullDesc,
                    version,
                    tigrisUrl, iconUrl, category
                })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Failed to create release.');

            setSuccess('');
            navigate('/', { replace: true, state: { flash: 'Plugin created successfully!' } });
        } catch (err) {
            setError(err.message);
            setSuccess('');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="animate-fade-in" style={{ maxWidth: '960px' }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
                <div>
                    <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--text-primary)', fontSize: '0.85rem', fontWeight: 500, marginBottom: '8px' }}>
                        <ArrowLeft size={14} /> Back to dashboard
                    </Link>
                    <h1 style={{ fontSize: '1.75rem', fontWeight: 400 }}>Create plugin</h1>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Enter details and upload your plugin archive for review.</p>
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button type="button" className="btn-secondary" onClick={() => navigate(-1)}>Discard</button>
                    <button type="button" className="btn-primary" onClick={handleSubmit} disabled={uploading}>
                        {uploading ? 'Processing...' : 'Create release'}
                    </button>
                </div>
            </div>

            {error && <div className="banner-error">{error}</div>}
            {success && <div className="banner-success">⏳ {success}</div>}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: '32px' }}>
                <form id="upload-form" onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
                    
                    {/* App Details Section */}
                    <div className="glass-panel">
                        <h2 style={{ fontSize: '1.1rem', fontWeight: 500, marginBottom: '24px' }}>Plugin Details</h2>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                            <div>
                                <label className="input-label">Plugin name *</label>
                                <input className="input-field" type="text" value={name} onChange={e => setName(e.target.value)}
                                    placeholder="e.g. Workspace Organizer" required maxLength={60} />
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>{name.length}/60</div>
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                                <div>
                                    <label className="input-label">Category *</label>
                                    <select className="input-field" value={category} onChange={e => setCategory(e.target.value)}>
                                        {CATEGORIES.map(c => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
                                    </select>
                                </div>
                                <div>
                                    <label className="input-label">Release version *</label>
                                    <input className="input-field" type="text" value={version} onChange={e => setVersion(e.target.value)}
                                        placeholder="1.0.0" required />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Release Archive Section */}
                    <div className="glass-panel">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                            <h2 style={{ fontSize: '1.1rem', fontWeight: 500 }}>Plugin Bundle</h2>
                        </div>
                        
                        <div style={{ 
                            border: '2px dashed var(--border)', borderRadius: '8px', padding: '32px', textAlign: 'center',
                            background: pluginFile ? 'var(--accent-light)' : 'transparent', cursor: 'pointer'
                        }} onClick={() => pluginRef.current?.click()}>
                            <input type="file" ref={pluginRef} accept=".zip" onChange={e => setPluginFile(e.target.files?.[0] || null)} style={{ display: 'none' }} />
                            {pluginFile ? (
                                <div>
                                    <CheckCircle size={32} color="var(--success)" style={{ margin: '0 auto 12px' }} />
                                    <div style={{ fontWeight: 500, fontSize: '0.9rem' }}>{pluginFile.name}</div>
                                    <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{(pluginFile.size / 1024 / 1024).toFixed(2)} MB</div>
                                    <div style={{ color: 'var(--text-primary)', fontSize: '0.8rem', mt: '8px' }}>Click to change archive</div>
                                </div>
                            ) : (
                                <div>
                                    <UploadCloud size={32} color="var(--text-muted)" style={{ margin: '0 auto 12px' }} />
                                    <div style={{ fontWeight: 500, fontSize: '0.95rem' }}>Upload .zip bundle</div>
                                    <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', maxWidth: '300px', margin: '8px auto 0' }}>
                                        Upload the compiled plugin bundle. Only .zip archives are accepted for release.
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Store Listing Section */}
                    <div className="glass-panel">
                        <h2 style={{ fontSize: '1.1rem', fontWeight: 500, marginBottom: '24px' }}>Store Presence</h2>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                            <div>
                                <label className="input-label">Short description *</label>
                                <input className="input-field" type="text" value={shortDesc} onChange={e => setShortDesc(e.target.value)}
                                    placeholder="One sentence that summarizes what it does" required maxLength={80} />
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>{shortDesc.length}/80</div>
                            </div>

                            <div>
                                <label className="input-label">Full description</label>
                                <textarea className="input-field" value={fullDesc} onChange={e => setFullDesc(e.target.value)}
                                    placeholder="Provide more details about features and usage..." rows={6} />
                            </div>

                            <div>
                                <label className="input-label">App icon</label>
                                <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                                    <div style={{ 
                                        width: 80, height: 80, borderRadius: 16, border: '1px solid var(--border)',
                                        background: 'var(--bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden'
                                    }}>
                                        {iconPreview ? <img src={iconPreview} style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : <Image size={24} color="var(--border)" />}
                                    </div>
                                    <div>
                                        <input type="file" ref={iconRef} accept="image/*" onChange={handleIconChange} style={{ display: 'none' }} />
                                        <button type="button" className="btn-secondary" onClick={() => iconRef.current?.click()} style={{ fontSize: '0.8rem' }}>
                                            {iconFile ? 'Change icon' : 'Upload icon'}
                                        </button>
                                        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '8px' }}>512×512 PNG or JPG. Max 1MB.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </form>

                {/* Info Sidebar */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    <div className="glass-panel" style={{ border: 'none', background: 'var(--border-light)' }}>
                        <div style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
                            <Info size={18} color="var(--text-muted)" />
                            <h3 style={{ fontSize: '0.9rem', fontWeight: 600 }}>Review Process</h3>
                        </div>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                            All releases are reviewed by our safety team. This usually takes 24-48 hours. Ensure your plugin adheres to the <a href="#" style={{ color: 'var(--text-primary)' }}>Developer Guidelines</a>.
                        </p>
                    </div>

                    <div className="glass-panel" style={{ border: 'none', background: 'var(--bg)' }}>
                        <div style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
                            <HelpCircle size={18} color="var(--text-muted)" />
                            <h3 style={{ fontSize: '0.9rem', fontWeight: 600 }}>Need help?</h3>
                        </div>
                        <ul style={{ fontSize: '0.8rem', color: 'var(--text-muted)', paddingLeft: '20px', marginBottom: 0 }}>
                            <li style={{ marginBottom: '8px' }}>How to bundle plugins</li>
                            <li style={{ marginBottom: '8px' }}>Setting up store listing</li>
                            <li>Monetization guide</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}
