import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Package, ShoppingBag, Settings, Code, BarChart3, HelpCircle } from 'lucide-react';

export default function Sidebar() {
    const location = useLocation();

    const menuItems = [
        { label: 'Dashboard', icon: <LayoutDashboard size={20} />, path: '/' },
        { label: 'All Plugins', icon: <Package size={20} />, path: '/plugins' },
        { section: 'Store Presence' },
        { label: 'Store Listing', icon: <ShoppingBag size={20} />, path: '/store-listing' },
        { label: 'App Content', icon: <BarChart3 size={20} />, path: '/app-content' },
        { section: 'Development' },
        { label: 'API Access', icon: <Code size={20} />, path: '/api-access' },
        { label: 'Settings', icon: <Settings size={20} />, path: '/settings' },
    ];

    return (
        <aside className="sidebar">
            <nav className="sidebar-nav">
                {menuItems.map((item, index) => {
                    if (item.section) {
                        return <div key={index} className="section-label">{item.section}</div>;
                    }

                    const isActive = location.pathname === item.path;
                    return (
                        <Link
                            key={item.label}
                            to={item.path}
                            className={`sidebar-item ${isActive ? 'active' : ''}`}
                        >
                            {item.icon}
                            <span>{item.label}</span>
                        </Link>
                    );
                })}
            </nav>
            
            <div style={{ marginTop: 'auto', padding: '24px' }}>
                <Link to="/help" className="sidebar-item">
                    <HelpCircle size={20} />
                    <span>Support</span>
                </Link>
            </div>
        </aside>
    );
}
