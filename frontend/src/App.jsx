import { useState, useEffect } from 'react';
import Header from './components/Header';
import CategoryFilter from './components/CategoryFilter';
import PostCard from './components/PostCard';
import PostDetail from './components/PostDetail';
import AdminDashboard from './components/AdminDashboard';
import Login from './components/Login';
import Signup from './components/Signup';
import PostCreate from './components/PostCreate';
import './index.css';

const API_URL = 'http://localhost:8000';

function App() {
  // Data State
  const [posts, setPosts] = useState([]);
  const [categories, setCategories] = useState({ primary: [], secondary: [] });

  // Filter State
  const [selectedPrimary, setSelectedPrimary] = useState([]);
  const [selectedSecondary, setSelectedSecondary] = useState([]);
  const [filterLogic, setFilterLogic] = useState('AND'); // 'AND' or 'OR'
  const [selectedVideoType, setSelectedVideoType] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Auth State
  const [currentUser, setCurrentUser] = useState(null);

  // UI State
  const [showLogin, setShowLogin] = useState(false);
  const [showSignup, setShowSignup] = useState(false);
  const [showAdminDashboard, setShowAdminDashboard] = useState(false);
  const [showPostCreate, setShowPostCreate] = useState(false);
  const [selectedPost, setSelectedPost] = useState(null);
  const [loading, setLoading] = useState(false);

  // Initial Auth Check
  useEffect(() => {
    const checkAuth = async () => {
      const token = sessionStorage.getItem('token');
      const userStr = sessionStorage.getItem('user');

      if (token && userStr) {
        setCurrentUser(JSON.parse(userStr));
      } else {
        setShowLogin(true); // Force login if not authenticated
      }
    };
    checkAuth();
  }, []);

  // Fetch Data only when authenticated
  useEffect(() => {
    if (currentUser) {
      fetchPosts();
      fetchCategories();
    }
  }, [currentUser]);

  const fetchPosts = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/posts`);
      const data = await response.json();
      setPosts(data);
    } catch (error) {
      console.error('Failed to fetch posts:', error);
    } finally {
      setLoading(false);
    }
  };

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
    sessionStorage.setItem('token', token);
    sessionStorage.setItem('user', JSON.stringify(user));
    setCurrentUser(user);
    setShowLogin(false);
    setShowSignup(false);
  };

  const handleLogout = () => {
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    setCurrentUser(null);
    setShowAdminDashboard(false);
    setShowPostCreate(false);
    setSelectedPost(null);
    setShowLogin(true); // Show login modal immediately after logout
  };

  const filteredPosts = posts.filter(post => {
    // 1. Video Type Filter
    const matchesVideoType = selectedVideoType === 'all' || post.video_type === selectedVideoType;

    // 2. Search Filter
    const matchesSearch = post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (post.description && post.description.toLowerCase().includes(searchQuery.toLowerCase()));

    // 3. Category Filter
    let matchesCategory = true;

    // Helper to check if post has ANY of the selected categories (OR logic base for single group)
    // But user wants AND logic across multiple selections if configured.

    const postPrimary = post.primary_categories || [];
    const postSecondary = post.secondary_categories || [];

    // Combine selected categories for easier logic if we treat them as a single pool, 
    // BUT user asked to separate them. Let's check requirements: "Separate Primary and Secondary... Multi-select... AND logic".
    // Usually AND logic means: Post must have Primary A AND Primary B (if both selected).
    // OR logic means: Post must have Primary A OR Primary B.

    // Primary Filter
    let matchesPrimary = true;
    if (selectedPrimary.length > 0) {
      if (filterLogic === 'AND') {
        // Post must have ALL selected primary categories
        matchesPrimary = selectedPrimary.every(id => postPrimary.includes(id));
      } else {
        // Post must have AT LEAST ONE selected primary category
        matchesPrimary = selectedPrimary.some(id => postPrimary.includes(id));
      }
    }

    // Secondary Filter
    let matchesSecondary = true;
    if (selectedSecondary.length > 0) {
      if (filterLogic === 'AND') {
        matchesSecondary = selectedSecondary.every(id => postSecondary.includes(id));
      } else {
        matchesSecondary = selectedSecondary.some(id => postSecondary.includes(id));
      }
    }

    matchesCategory = matchesPrimary && matchesSecondary;

    return matchesCategory && matchesVideoType && matchesSearch;
  });

  const getCategoryName = (id, type) => {
    const list = type === 'primary' ? categories.primary : categories.secondary;
    const cat = list.find(c => c.id === id);
    return cat ? cat.name : '';
  };

  return (
    <div className="app">
      <Header
        onSearch={setSearchQuery}
        onAdminClick={() => setShowAdminDashboard(true)}
        onCreateClick={() => setShowPostCreate(true)}
        currentUser={currentUser}
        onLoginClick={() => setShowLogin(true)}
        onLogoutClick={handleLogout}
      />

      <main className="container">
        {currentUser ? (
          <>
            <CategoryFilter
              categories={categories}
              selectedPrimary={selectedPrimary}
              onSelectPrimary={setSelectedPrimary}
              selectedSecondary={selectedSecondary}
              onSelectSecondary={setSelectedSecondary}
              filterLogic={filterLogic}
              onToggleLogic={setFilterLogic}
              selectedVideoType={selectedVideoType}
              onSelectVideoType={setSelectedVideoType}
            />

            {loading ? (
              <div className="loading-container">
                <div className="spinner"></div>
              </div>
            ) : (
              <div className="grid">
                {filteredPosts.map(post => (
                  <PostCard
                    key={post.id}
                    post={post}
                    onClick={() => setSelectedPost(post)}
                    getCategoryName={getCategoryName}
                  />
                ))}
              </div>
            )}

            {filteredPosts.length === 0 && !loading && (
              <div className="text-center" style={{ padding: '4rem', color: 'var(--text-secondary)' }}>
                <h3>No references found</h3>
                <p>Try adjusting your filters or search query</p>
              </div>
            )}
          </>
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

      {selectedPost && (
        <PostDetail
          postId={selectedPost.id}
          onClose={() => setSelectedPost(null)}
          onUpdate={fetchPosts}
        />
      )}

      {showPostCreate && (
        <PostCreate
          onClose={() => setShowPostCreate(false)}
          onPostCreated={fetchPosts}
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
              // Only show close button if user is already logged in (optional, but here we force login)
              // Actually, if we force login, we might not want a close button if they are not logged in.
              // But let's keep it simple.
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
  );
}

export default App;
