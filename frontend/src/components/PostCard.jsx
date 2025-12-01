import React, { forwardRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { API_URL } from '../config';

const PostCard = forwardRef(({ post, onClick, getCategoryName }, ref) => {
    const [isFavorited, setIsFavorited] = useState(post.is_favorited);

    const handleFavorite = async (e) => {
        e.preventDefault(); // Prevent Link navigation
        e.stopPropagation(); // Prevent card click
        try {
            const token = localStorage.getItem('token');
            if (!token) return;

            const response = await fetch(`${API_URL}/api/posts/${post.id}/favorite`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setIsFavorited(data.is_favorited);
            }
        } catch (error) {
            console.error('Failed to toggle favorite:', error);
        }
    };

    return (
        <Link
            to={`/post/${post.id}`}
            className="post-card-link"
            onClick={(e) => {
                // If Ctrl/Cmd key is pressed, let it open in new tab (default behavior)
                // Otherwise, prevent default navigation and open modal
                if (!e.ctrlKey && !e.metaKey && !e.shiftKey && e.button === 0) {
                    e.preventDefault();
                    onClick();
                }
            }}
            style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}
        >
            <div className="post-card" ref={ref}>
                <div className="thumbnail-container">
                    <img
                        src={post.thumbnail}
                        alt={post.title}
                        className="post-thumbnail"
                        loading="lazy"
                    />
                    <span className={`badge ${post.video_type === 'long' ? 'badge-long' : 'badge-short'} video-type-badge`}>
                        {post.video_type === 'long' ? '📺 Long' : '📱 Short'}
                    </span>
                    <button
                        className={`favorite-btn ${isFavorited ? 'active' : ''}`}
                        onClick={handleFavorite}
                        style={{ position: 'absolute', top: '8px', left: '8px', zIndex: 10, background: 'rgba(0,0,0,0.5)', borderRadius: '50%' }}
                    >
                        {isFavorited ? '⭐' : '☆'}
                    </button>
                </div>

                <div className="post-content">
                    <h3 className="post-title" title={post.title}>{post.title}</h3>

                    <div className="post-tags">
                        {post.industry_categories && post.industry_categories.slice(0, 2)
                            .map(id => ({ id, name: getCategoryName(id, 'industry') }))
                            .map(cat => (
                                <span key={cat.id} className="badge badge-primary">
                                    {cat.name}
                                </span>
                            ))}
                        {post.genre_categories && post.genre_categories.slice(0, 2)
                            .map(id => ({ id, name: getCategoryName(id, 'genre') }))
                            .map(cat => (
                                <span key={cat.id} className="badge badge-secondary">
                                    {cat.name}
                                </span>
                            ))}
                        {post.cast_categories && post.cast_categories.slice(0, 1)
                            .map(id => ({ id, name: getCategoryName(id, 'cast') }))
                            .map(cat => (
                                <span key={cat.id} className="badge badge-secondary" style={{ background: '#e0f2f1', color: '#00695c' }}>
                                    {cat.name}
                                </span>
                            ))}
                        {post.mood_categories && post.mood_categories.slice(0, 1)
                            .map(id => ({ id, name: getCategoryName(id, 'mood') }))
                            .map(cat => (
                                <span key={cat.id} className="badge badge-secondary" style={{ background: '#f3e5f5', color: '#7b1fa2' }}>
                                    {cat.name}
                                </span>
                            ))}
                        {post.editing_categories && post.editing_categories.slice(0, 1)
                            .map(id => ({ id, name: getCategoryName(id, 'editing') }))
                            .map(cat => (
                                <span key={cat.id} className="badge badge-secondary" style={{ background: '#fff3e0', color: '#e65100' }}>
                                    {cat.name}
                                </span>
                            ))}
                    </div>

                    <div className="post-footer">
                        <span className="post-author">👤 {post.author_name || 'Unknown'}</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                            <span className="post-views">👁️ {post.view_count?.toLocaleString() || 0}</span>
                            <span className="post-date">{new Date(post.created_at).toLocaleDateString()}</span>
                        </div>
                    </div>
                </div>
            </div>
        </Link>
    );
});

export default PostCard;
