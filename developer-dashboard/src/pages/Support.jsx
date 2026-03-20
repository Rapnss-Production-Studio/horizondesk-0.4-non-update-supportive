import { useState } from 'react';
import { HelpCircle, ChevronDown, FileText, ExternalLink, Send, Check, BookOpen, MessageCircle } from 'lucide-react';

const FAQ_ITEMS = [
    {
        q: 'How do I publish my first plugin?',
        a: 'Navigate to the "Create plugin" page, fill in the details, upload your .zip bundle, and submit. Your plugin will be reviewed within 24-48 hours.'
    },
    {
        q: 'What file format should my plugin be?',
        a: 'Plugins must be uploaded as .zip archives containing a main.py with a register_tools function and a horizon_plugin.raf metadata file.'
    },
    {
        q: 'How much does it cost to publish?',
        a: 'Your first release is free! After that, each release costs $2.00, which is deducted from your Ad Credit balance.'
    },
    {
        q: 'Can I update an existing plugin?',
        a: 'Yes! Go to All Plugins, click Edit on your plugin, update the details, and save. For new versions, create a new release from the Upload page.'
    },
    {
        q: 'How do I publish from the CLI?',
        a: 'Install the SDK with "pip install horizondesk", then run "horizondesk login" to authenticate, and "horizondesk publish" from your plugin directory.'
    },
    {
        q: 'What data can my plugin access?',
        a: 'Plugins run inside the Horizon Desk agent sandbox. They can access tools registered via the SDK but cannot directly access user files or keys without explicit permission.'
    },
];

const DOCS_LINKS = [
    { label: 'Getting Started Guide', url: 'https://github.com/rapnss/horizondesk-sdk', icon: <BookOpen size={16} /> },
    { label: 'Plugin SDK Reference', url: 'https://github.com/rapnss/horizondesk-sdk', icon: <FileText size={16} /> },
    { label: 'Developer Guidelines', url: 'https://github.com/rapnss/horizondesk-sdk', icon: <FileText size={16} /> },
    { label: 'API Documentation', url: 'https://github.com/rapnss/horizondesk-sdk', icon: <FileText size={16} /> },
];

export default function Support() {
    const [openFaq, setOpenFaq] = useState(null);
    const [contactForm, setContactForm] = useState({ subject: '', message: '' });
    const [submitted, setSubmitted] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!contactForm.subject || !contactForm.message) return;
        setSubmitted(true);
        setContactForm({ subject: '', message: '' });
        setTimeout(() => setSubmitted(false), 4000);
    };

    return (
        <div className="animate-fade-in" style={{ maxWidth: '800px' }}>
            <div style={{ marginBottom: '32px' }}>
                <h1 style={{ fontSize: '1.75rem', fontWeight: 400 }}>Support</h1>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Find answers, documentation, and contact our team</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: '24px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    {/* FAQ */}
                    <div className="glass-panel">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                            <HelpCircle size={18} color="var(--text-primary)" />
                            <h2 style={{ fontSize: '1.1rem', fontWeight: 500 }}>Frequently Asked Questions</h2>
                        </div>
                        <div className="accordion">
                            {FAQ_ITEMS.map((item, i) => (
                                <div key={i} className="accordion-item">
                                    <button className="accordion-trigger" onClick={() => setOpenFaq(openFaq === i ? null : i)}>
                                        <span>{item.q}</span>
                                        <ChevronDown size={16} style={{ transform: openFaq === i ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
                                    </button>
                                    {openFaq === i && (
                                        <div className="accordion-content">
                                            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.6 }}>{item.a}</p>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Contact Form */}
                    <div className="glass-panel">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                            <MessageCircle size={18} color="var(--accent)" />
                            <h2 style={{ fontSize: '1.1rem', fontWeight: 500 }}>Contact Us</h2>
                        </div>

                        {submitted ? (
                            <div style={{ textAlign: 'center', padding: '32px' }}>
                                <Check size={48} color="var(--success)" style={{ marginBottom: '12px' }} />
                                <p style={{ fontWeight: 500 }}>Message sent!</p>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>We'll get back to you within 24 hours.</p>
                            </div>
                        ) : (
                            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                                <div>
                                    <label className="input-label">Subject</label>
                                    <input className="input-field" value={contactForm.subject}
                                        onChange={e => setContactForm({ ...contactForm, subject: e.target.value })}
                                        placeholder="Brief description of your issue" required />
                                </div>
                                <div>
                                    <label className="input-label">Message</label>
                                    <textarea className="input-field" rows={5} value={contactForm.message}
                                        onChange={e => setContactForm({ ...contactForm, message: e.target.value })}
                                        placeholder="Describe your issue in detail..." required />
                                </div>
                                <button type="submit" className="btn-primary" style={{ alignSelf: 'flex-start', padding: '10px 20px' }}>
                                    <Send size={16} /> Send message
                                </button>
                            </form>
                        )}
                    </div>
                </div>

                {/* Sidebar: Documentation Links */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    <div className="glass-panel">
                        <h3 style={{ fontSize: '1rem', fontWeight: 500, marginBottom: '16px' }}>Documentation</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            {DOCS_LINKS.map((link, i) => (
                                <a key={i} href={link.url} target="_blank" rel="noopener noreferrer"
                                    style={{
                                        display: 'flex', alignItems: 'center', gap: '10px', padding: '10px 12px',
                                        borderRadius: '6px', fontSize: '0.85rem', color: 'var(--text)',
                                        transition: 'background 0.2s'
                                    }}
                                    className="doc-link">
                                    {link.icon}
                                    <span style={{ flex: 1 }}>{link.label}</span>
                                    <ExternalLink size={14} color="var(--text-muted)" />
                                </a>
                            ))}
                        </div>
                    </div>

                    <div className="glass-panel" style={{ background: 'var(--accent-light)', border: 'none' }}>
                        <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>Need urgent help?</h3>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                            Email us at <a href="mailto:support@rapnss.in" style={{ color: 'var(--text-primary)', fontWeight: 500 }}>support@rapnss.in</a> for priority support.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
