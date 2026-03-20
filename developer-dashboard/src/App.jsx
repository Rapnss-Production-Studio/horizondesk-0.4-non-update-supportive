import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import UploadPlugin from './pages/UploadPlugin';
import Onboarding from './pages/Onboarding';
import OAuthCallback from './pages/OAuthCallback';
import AllPlugins from './pages/AllPlugins';
import StoreListing from './pages/StoreListing';
import AppContent from './pages/AppContent';
import ApiAccess from './pages/ApiAccess';
import SettingsPage from './pages/SettingsPage';
import Support from './pages/Support';

// Protect routes that require login and Developer T&C acceptance
const PublishRoute = ({ children }) => {
  const { user, developerInfo, loading } = useAuth();

  if (loading) return <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Loading...</div>;
  if (!user) return <Navigate to="/onboarding" replace />;
  if (!developerInfo) return <Navigate to="/onboarding" replace />;

  return children;
};

// Route wrapper for onboarding (includes login)
const OnboardingRoute = ({ children }) => {
  const { developerInfo, loading } = useAuth();
  if (loading) return <div>Loading...</div>;
  if (developerInfo) return <Navigate to="/upload" replace />;
  return children;
};

function AppLayout() {
  const { user } = useAuth();
  
  return (
    <Router>
      <div className="app-container">
        <Navbar />
        <div className="main-wrapper">
          {user && <Sidebar />}
          <main className="main-content">
            <Routes>
              <Route path="/oauth/callback" element={<OAuthCallback />} />
              <Route path="/onboarding" element={<OnboardingRoute><Onboarding /></OnboardingRoute>} />
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload" element={<PublishRoute><UploadPlugin /></PublishRoute>} />
              <Route path="/plugins" element={<PublishRoute><AllPlugins /></PublishRoute>} />
              <Route path="/store-listing" element={<PublishRoute><StoreListing /></PublishRoute>} />
              <Route path="/app-content" element={<PublishRoute><AppContent /></PublishRoute>} />
              <Route path="/api-access" element={<PublishRoute><ApiAccess /></PublishRoute>} />
              <Route path="/settings" element={<PublishRoute><SettingsPage /></PublishRoute>} />
              <Route path="/help" element={<Support />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppLayout />
    </AuthProvider>
  );
}

export default App;
