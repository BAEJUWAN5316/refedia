import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Feed from './components/Feed';
import PostDetail from './components/PostDetail';
import AdminDashboard from './components/AdminDashboard';
import Login from './components/Login';
import Signup from './components/Signup';
import PostCreate from './components/PostCreate';
import './index.css';

import { API_URL } from './config';

function App() {
  // Auth State
  const [currentUser, setCurrentUser] = useState(null);

  // UI State - Global
  const [showLogin, setShowLogin] = useState(false);
  const [showSignup, setShowSignup] = useState(false);
  const [showAdminDashboard, setShowAdminDashboard] = useState(false);
  const [showPostCreate, setShowPostCreate] = useState(false);

  // Feed State (Lifted up to share with Header)
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState('all'); // 'all', 'my_posts', 'favorites'
  const [categories, setCategories] = useState({ primary: [], secondary: [] });
  const [feedKey, setFeedKey] = useState(0); // Key to force re-render of Feed

  // Initial Auth Check
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      const userStr = localStorage.getItem('user');

      if (token && userStr) {
        setCurrentUser(JSON.parse(userStr));
      } else {
        setShowLogin(true); // Force login if not authenticated
      }
    };
    checkAuth();
  }, []);

  // Fetch Categories (Global for AdminDashboard etc)
  useEffect(() => {
    if (currentUser) {
      fetchCategories();
    }
  }, [currentUser]);

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_URL}/api/categories`);
      const data = await response.json();
      setCategories(data);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const handleLogin = (user, token) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    setCurrentUser(user);
    setShowLogin(false);
    setShowSignup(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setCurrentUser(null);
    setShowAdminDashboard(false);
    setShowPostCreate(false);
    setShowLogin(true);
  };

  const handleLogoClick = () => {
    setSearchQuery('');
    setViewMode('all');
    setFeedKey(prev => prev + 1); // Force Feed to re-mount and reset its internal state
  };

  return (
    <Router>
      <div className="app">
        <Header
          onSearch={setSearchQuery}
          onAdminClick={() => setShowAdminDashboard(true)}
          onCreateClick={() => setShowPostCreate(true)}
          currentUser={currentUser}
          onLoginClick={() => setShowLogin(true)}
          onLogoutClick={handleLogout}
          viewMode={viewMode}
          onViewModeChange={setViewMode}
          onLogoClick={handleLogoClick}
        />

        <main className="container">
          {currentUser ? (
            <Routes>
              <Route path="/" element={
                <Feed
                  key={feedKey}
                  currentUser={currentUser}
                  viewMode={viewMode}
                  searchQuery={searchQuery}
                  onSearch={setSearchQuery}
                />
              } />
              <Route path="/post/:postId" element={
                <PostDetail
                  currentUser={currentUser}
                  onClose={undefined} // Let PostDetail handle navigation to '/'
                  onUpdate={() => { }} // No-op for standalone page for now, or reload
                />
              } />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          ) : (
            <div className="text-center" style={{ padding: '4rem', color: 'var(--text-secondary)' }}>
              <h3>Please login to view references</h3>
            </div>
          )}
        </main>

        {/* Modals */}
        {showAdminDashboard && (
          <AdminDashboard
            onClose={() => setShowAdminDashboard(false)}
            categories={categories}
            onCategoriesChanged={fetchCategories}
            currentUser={currentUser}
          />
        )}

        {showPostCreate && (
          <PostCreate
            onClose={() => setShowPostCreate(false)}
            onPostCreated={() => {
              // If on feed, trigger refresh? Feed handles its own fetch on mount/update.
              // Maybe we need a global refresh trigger or just let user refresh.
              // For now, simple close.
              window.location.reload(); // Simple way to refresh feed
            }}
          />
        )}

        {showLogin && (
          <div className="modal-overlay">
            <div className="modal-content-wrapper">
              <Login
                onLogin={handleLogin}
                onSwitchToSignup={() => {
                  setShowLogin(false);
                  setShowSignup(true);
                }}
              />
              {!currentUser && (
                <button className="modal-close-btn" onClick={() => setShowLogin(false)} style={{ display: 'none' }}>❌</button>
              )}
            </div>
          </div>
        )}

        {showSignup && (
          <div className="modal-overlay">
            <div className="modal-content-wrapper">
              <Signup
                onSwitchToLogin={() => {
                  setShowSignup(false);
                  setShowLogin(true);
                }}
              />
              <button className="modal-close-btn" onClick={() => setShowSignup(false)}>❌</button>
            </div>
          </div>
        )}
      </div>
    </Router>
  );
}

export default App;
