import { useState, useEffect, useRef, useCallback } from 'react';
import CategoryFilter from './CategoryFilter';
import PostCard from './PostCard';
import PostDetail from './PostDetail';
import { API_URL } from '../config';

export default function Feed({ currentUser, viewMode, searchQuery, onSearch }) {
    // Data State
    const [posts, setPosts] = useState([]);
    const [categories, setCategories] = useState({ primary: [], secondary: [] });

    // Filter State
    const [selectedPrimary, setSelectedPrimary] = useState([]);
    const [selectedSecondary, setSelectedSecondary] = useState([]);
    const [filterLogic, setFilterLogic] = useState('AND');
    const [selectedVideoType, setSelectedVideoType] = useState('all');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [seed, setSeed] = useState(null);

    // UI State
    const [selectedPost, setSelectedPost] = useState(null);
    const [loading, setLoading] = useState(false);

    // Pagination State
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);
    const observer = useRef();

    // Fetch Categories
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
                end_date: endDate,
                my_posts: viewMode === 'my_posts',
                favorites_only: viewMode === 'favorites'
            });

            if (seed) {
                params.append('seed', seed);
            }

            selectedPrimary.forEach(id => params.append('primary_category', id));
            selectedSecondary.forEach(id => params.append('secondary_category', id));

            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/posts?${params.toString()}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                if (response.status === 401 || response.status === 403) {
                    // Token expired or invalid - handled by App.jsx usually, but we can just fail here
                    // Ideally App.jsx handles logout. We can trigger a callback if needed.
                    return;
                }
                throw new Error('Failed to fetch posts');
            }

            const data = await response.json();

            if (pageNum === 1) {
                setPosts(Array.isArray(data) ? data : []);
            } else {
                setPosts(prev => [...prev, ...(Array.isArray(data) ? data : [])]);
            }
            setHasMore(Array.isArray(data) && data.length === 20);
        } catch (error) {
            console.error('Failed to fetch posts:', error);
            if (pageNum === 1) setPosts([]);
        } finally {
            setLoading(false);
        }
    }, [currentUser, selectedPrimary, selectedSecondary, filterLogic, selectedVideoType, searchQuery, startDate, endDate, viewMode, seed]);

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

    const getCategoryName = (id, type) => {
        const list = type === 'primary' ? categories.primary : categories.secondary;
        const cat = list.find(c => c.id === id);
        return cat ? cat.name : '';
    };

    const handleMix = () => {
        const newSeed = Math.floor(Math.random() * 1000000);
        setSeed(newSeed);
        setPage(1);
        // fetchPosts(1) will be triggered by useEffect dependency on seed/fetchPosts
    };

    const handleResetSort = () => {
        setSeed(null);
        setPage(1);
    };

    return (
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
                onMix={handleMix}
                onResetSort={handleResetSort}
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

            {selectedPost && (
                <PostDetail
                    postId={selectedPost.id}
                    currentUser={currentUser}
                    onClose={() => setSelectedPost(null)}
                    onUpdate={() => {
                        fetchPosts(1);
                        setPage(1);
                    }}
                />
            )}
        </>
    );
}
