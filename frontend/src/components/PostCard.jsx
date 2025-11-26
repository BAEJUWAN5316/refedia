import React, { forwardRef } from 'react';

const PostCard = forwardRef(({ post, onClick, getCategoryName }, ref) => {
    return (
        <div className="post-card" onClick={onClick} ref={ref}>
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
                    {post.primary_categories && post.primary_categories
                        .map(id => ({ id, name: getCategoryName(id, 'primary') }))
                        .sort((a, b) => a.name.localeCompare(b.name))
                        .map(cat => (
                            <span key={cat.id} className="badge badge-primary">
                                {cat.name}
                            </span>
                        ))}
                    {post.secondary_categories && post.secondary_categories
                        .map(id => ({ id, name: getCategoryName(id, 'secondary') }))
                        .sort((a, b) => a.name.localeCompare(b.name))
                        .map(cat => (
                            <span key={cat.id} className="badge badge-secondary">
                                {cat.name}
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
});

export default PostCard;
