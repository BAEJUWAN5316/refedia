import { useState, useEffect, useRef, useCallback } from 'react';
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
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // Auth State
  const [currentUser, setCurrentUser] = useState(null);

  // UI State
  const [showLogin, setShowLogin] = useState(false);
  const [showSignup, setShowSignup] = useState(false);
  const [showAdminDashboard, setShowAdminDashboard] = useState(false);
  const [showPostCreate, setShowPostCreate] = useState(false);
  const [selectedPost, setSelectedPost] = useState(null);
  const [loading, setLoading] = useState(false);

  // Pagination State
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const observer = useRef();

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
      fetchCategories();
    }
  }, [currentUser]);

  const fetchPosts = useCallback(async (pageNum) => {
    if (!currentUser) return;
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: pageNum,
        limit: 20,
        filter_logic: filterLogic,
        video_type: selectedVideoType !== 'all' ? selectedVideoType : '',
        search: searchQuery,
        start_date: startDate,
        end_date: endDate
      });

      selectedPrimary.forEach(id => params.append('primary_category', id));
      selectedSecondary.forEach(id => params.append('secondary_category', id));

      const response = await fetch(`${API_URL}/api/posts?${params.toString()}`);
      const data = await response.json();

      if (pageNum === 1) {
        setPosts(data);
      } else {
        setPosts(prev => [...prev, ...data]);
      }
      setHasMore(data.length === 20);
    } catch (error) {
      console.error('Failed to fetch posts:', error);
    } finally {
      setLoading(false);
    }
  }, [currentUser, selectedPrimary, selectedSecondary, filterLogic, selectedVideoType, searchQuery, startDate, endDate]);

  // Filter Change Effect
  useEffect(() => {
    if (currentUser) {
      setPage(1);
      fetchPosts(1);
    }
  }, [fetchPosts]);

  // Page Change Effect
  useEffect(() => {
    if (currentUser && page > 1) {
      fetchPosts(page);
    }
  }, [page, fetchPosts, currentUser]);

  // Infinite Scroll Ref
  const lastPostElementRef = useCallback(node => {
    if (loading) return;
    if (observer.current) observer.current.disconnect();
    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        setPage(prevPage => prevPage + 1);
      }
    });
    if (node) observer.current.observe(node);
  }, [loading, hasMore]);

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
              startDate={startDate}
              onStartDateChange={setStartDate}
              endDate={endDate}
              onEndDateChange={setEndDate}
            />

            {loading && page === 1 ? (
              <div className="loading-container">
                <div className="spinner"></div>
              </div>
            ) : (
              <div className="grid">
                {posts.map((post, index) => {
                  if (posts.length === index + 1) {
                    return (
                      <PostCard
                        ref={lastPostElementRef}
                        key={post.id}
                        post={post}
                        onClick={() => setSelectedPost(post)}
                        getCategoryName={getCategoryName}
                      />
                    );
                  } else {
                    return (
                      <PostCard
                        key={post.id}
                        post={post}
                        onClick={() => setSelectedPost(post)}
                        getCategoryName={getCategoryName}
                      />
                    );
                  }
                })}
              </div>
            )}
            {loading && page > 1 && (
              <div className="loading-container" style={{ height: '100px' }}>
                <div className="spinner"></div>
              </div>
            )}

            {posts.length === 0 && !loading && (
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

      {showPostCreate && (
        <PostCreate
          onClose={() => setShowPostCreate(false)}
          onPostCreated={() => {
            fetchPosts(1);
            setPage(1);
          }}
        />
      )}

      {selectedPost && (
        <PostDetail
          postId={selectedPost.id}
          currentUser={currentUser}
          onClose={() => setSelectedPost(null)}
          onUpdate={fetchPosts}
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
