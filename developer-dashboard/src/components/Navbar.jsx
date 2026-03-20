import { useAuth } from '../context/AuthContext';
import { LogOut, User, Bell } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Navbar() {
    const { user, logout } = useAuth();

    return (
        <nav className="navbar animate-fade-in">
            <Link to="/" className="nav-brand">
                <img src="https://images-rapnss.t3.storage.dev/512-icon-9.png" alt="Horizon Desk" />
                <span>Horizon</span>
                <span style={{ color: 'var(--border)', margin: '0 8px' }}>|</span>
                <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Play Console</span>
            </Link>

            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <button className="btn-secondary" style={{ border: 'none', padding: '8px' }}>
                    <Bell size={20} color="var(--text-muted)" />
                </button>
                
                {user ? (
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginLeft: '12px' }}>
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                            <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>{user.username}</span>
                            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Developer</span>
                        </div>
                        <div style={{ 
                            width: 32, height: 32, borderRadius: '50%', background: 'var(--accent-light)', 
                            display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent)'
                        }}>
                            <User size={18} />
                        </div>
                        <button onClick={logout} className="btn-secondary" title="Logout" style={{ border: 'none', padding: '8px' }}>
                            <LogOut size={18} color="var(--text-muted)" />
                        </button>
                    </div>
                ) : null}
            </div>
        </nav>
    );
}
