import React from 'react';

export default function PostCard({ post, onClick, getCategoryName }) {
    return (
        <div className="post-card" onClick={onClick}>
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
            </div>

            <div className="post-content">
                <h3 className="post-title" title={post.title}>{post.title}</h3>

                <div className="post-tags">
                    {post.primary_categories && post.primary_categories.map(catId => (
                        <span key={catId} className="badge badge-primary">
                            {getCategoryName(catId, 'primary')}
                        </span>
                    ))}
                    {post.secondary_categories && post.secondary_categories.map(catId => (
                        <span key={catId} className="badge badge-secondary">
                            {getCategoryName(catId, 'secondary')}
                        </span>
                    ))}
                </div>

                <div className="post-footer">
                    <span className="post-author">👤 {post.author_name || 'Unknown'}</span>
                    <span className="post-date">{new Date(post.created_at).toLocaleDateString()}</span>
                </div>
            </div>
        </div>
    );
}
