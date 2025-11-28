import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import CategorySelector from './CategorySelector';
import { API_URL } from '../config';

export default function PostDetail({ postId: propPostId, currentUser, onClose, onUpdate }) {
    const { postId: paramPostId } = useParams();
    const navigate = useNavigate();
    const postId = propPostId || paramPostId;
    const isModal = !!propPostId; // If prop is provided, it's a modal

    const [post, setPost] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editedTitle, setEditedTitle] = useState('');
    const [editedMemo, setEditedMemo] = useState('');
    const [editedPrimary, setEditedPrimary] = useState([]);
    const [editedSecondary, setEditedSecondary] = useState([]);
    const [editedVideoType, setEditedVideoType] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [categories, setCategories] = useState({ primary: [], secondary: [] });
    const [copyUrlText, setCopyUrlText] = useState('Copy');
    const [isSaving, setIsSaving] = useState(false);
    const [isThumbnailCopied, setIsThumbnailCopied] = useState(false);
    const [isFavorited, setIsFavorited] = useState(false);

    useEffect(() => {
        if (postId) {
            fetchPost();
            fetchCategories();
        }
    }, [postId]);

    const fetchPost = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
            const response = await fetch(`${API_URL}/api/posts/${postId}`, { headers });
            if (!response.ok) throw new Error('Failed to fetch post');
            const data = await response.json();
            setPost(data);
            setEditedTitle(data.title);
            setEditedMemo(data.memo || '');
            setEditedPrimary(data.primary_categories || []);
            setEditedSecondary(data.secondary_categories || []);
            setEditedVideoType(data.video_type || 'short');
            setIsFavorited(data.is_favorited);
        } catch (err) {
            setError(err.message);
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

    const getCategoryName = (id, type) => {
        const list = type === 'primary' ? categories.primary : categories.secondary;
        const cat = list.find(c => c.id === id);
        return cat ? cat.name : id;
    };

    const getYouTubeEmbedUrl = (url) => {
        if (!url) return '';
        let videoId = '';

        // Handle various YouTube URL formats
        const patterns = [
            /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|youtube\.com\/shorts\/)([^#&?]*)/,
            /^([^#&?]*)$/ // Fallback if it's just the ID
        ];

        for (const pattern of patterns) {
            const match = url.match(pattern);
            if (match && match[1]) {
                videoId = match[1];
                break;
            }
        }

        return `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=0`;
    };

    const handleUpdate = async () => {
        if (!editedTitle.trim()) {
            alert('Title is required');
            return;
        }

        setIsSaving(true);
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/posts/${postId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    title: editedTitle,
                    memo: editedMemo,
                    primary_categories: editedPrimary,
                    secondary_categories: editedSecondary,
                    video_type: editedVideoType
                })
            });

            if (!response.ok) throw new Error('Failed to update post');

            const updatedPost = await response.json();
            setPost(updatedPost);
            setIsEditing(false);
            if (onUpdate) onUpdate(updatedPost);
        } catch (err) {
            alert(err.message);
        } finally {
            setIsSaving(false);
        }
    };

    const handleDelete = async () => {
        if (!window.confirm('Are you sure you want to delete this post?')) return;

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/posts/${postId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) throw new Error('Failed to delete post');

            if (onClose) onClose();
            else navigate('/'); // Navigate back if standalone

            if (onUpdate) onUpdate(null); // Trigger refresh in parent
        } catch (err) {
            alert(err.message);
        }
    };

    const handleFavorite = async () => {
        try {
            const token = localStorage.getItem('token');
            if (!token) return;

            const response = await fetch(`${API_URL}/api/posts/${postId}/favorite`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setIsFavorited(data.is_favorited);
                if (onUpdate) onUpdate({ ...post, is_favorited: data.is_favorited });
            }
        } catch (error) {
            console.error('Failed to toggle favorite:', error);
        }
    };

    const handleCopyUrl = () => {
        navigator.clipboard.writeText(post.url).then(() => {
            setCopyUrlText('Copied!');
            setTimeout(() => setCopyUrlText('Copy'), 2000);
        });
    };

    const handleCopyImage = async () => {
        try {
            const response = await fetch(`${API_URL}/api/download/image?url=${encodeURIComponent(post.thumbnail)}`);
            if (!response.ok) throw new Error('Failed to fetch image');

            const blob = await response.blob();

            // Convert to PNG if necessary (Clipboard API often requires PNG)
            if (blob.type === 'image/jpeg' || blob.type === 'image/jpg') {
                const img = new Image();
                img.src = URL.createObjectURL(blob);
                await new Promise((resolve, reject) => {
                    img.onload = resolve;
                    img.onerror = reject;
                });

                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);

                canvas.toBlob(async (pngBlob) => {
                    try {
                        await navigator.clipboard.write([
                            new ClipboardItem({
                                [pngBlob.type]: pngBlob
                            })
                        ]);
                        setIsThumbnailCopied(true);
                        setTimeout(() => setIsThumbnailCopied(false), 2000);
                        URL.revokeObjectURL(img.src);
                    } catch (err) {
                        console.error('Failed to write PNG to clipboard:', err);
                        alert('Failed to copy image to clipboard');
                    }
                }, 'image/png');
            } else {
                // Try writing directly if it's already PNG or other supported type
                await navigator.clipboard.write([
                    new ClipboardItem({
                        [blob.type]: blob
                    })
                ]);
                setIsThumbnailCopied(true);
                setTimeout(() => setIsThumbnailCopied(false), 2000);
            }
        } catch (err) {
            console.error('Failed to copy image:', err);
            alert('Failed to copy image to clipboard: ' + err.message);
        }
    };

    const handleDownloadThumbnail = async () => {
        try {
            const response = await fetch(`${API_URL}/api/download/image?url=${encodeURIComponent(post.thumbnail)}`);
            if (!response.ok) throw new Error('Failed to download image');
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `thumbnail-${post.id}.jpg`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error('Failed to download thumbnail:', err);
            alert('Failed to download thumbnail');
        }
    };

    if (loading) return <div className="loading-container"><div className="spinner"></div></div>;
    if (error) return <div className="text-center text-danger">{error}</div>;
    if (!post) return null;

    const embedUrl = getYouTubeEmbedUrl(post.url);

    const content = (
        <div className={isModal ? "modal" : "container"} style={isModal ? { maxWidth: '1000px', width: '90%', height: '90vh', display: 'flex', flexDirection: 'column', padding: '0' } : { maxWidth: '1000px', margin: '2rem auto', padding: '0', background: 'var(--bg-secondary)', borderRadius: '12px', border: '1px solid var(--border-color)' }} onClick={e => e.stopPropagation()}>
            {/* Header */}
            <div className="modal-header" style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div style={{ flex: 1 }}>
                    <h3 className="modal-title" style={{ fontSize: '1.2rem', fontWeight: '600', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        {isEditing ? 'Edit Reference' : (
                            <>
                                {post.title}
                                <button
                                    className={`favorite-btn ${isFavorited ? 'active' : ''}`}
                                    onClick={handleFavorite}
                                    title={isFavorited ? "Remove from favorites" : "Add to favorites"}
                                >
                                    {isFavorited ? '⭐' : '☆'}
                                </button>
                            </>
                        )}
                    </h3>
                    {!isEditing && (
                        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
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
                            <span className={`badge ${post.video_type === 'long' ? 'badge-long' : 'badge-short'}`}>
                                {post.video_type === 'long' ? '📺 Long Form' : '📱 Short Form'}
                            </span>
                        </div>
                    )}
                </div>
                <button className="btn btn-icon" onClick={onClose || (() => navigate('/'))} style={{ background: 'transparent', border: 'none', fontSize: '1.2rem', cursor: 'pointer', marginLeft: '1rem' }}>
                    ❌
                </button>
            </div>

            <div className="modal-body" style={{ flex: 1, overflowY: 'auto', padding: '2rem' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>

                    {/* 1. Playable YouTube Screen */}
                    <div style={{ width: '100%' }}>
                        <div style={{ position: 'relative', paddingTop: '56.25%', background: '#000', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 4px 20px rgba(0,0,0,0.3)' }}>
                            <iframe
                                src={embedUrl}
                                style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none' }}
                                allowFullScreen
                            />
                        </div>
                    </div>

                    {/* 2. Thumbnail & 3. URL */}
                    <div className="grid grid-2" style={{ gap: '1.5rem', alignItems: 'start' }}>
                        <div className="card" style={{ padding: '1.5rem' }}>
                            <h4 style={{ marginBottom: '1rem', fontSize: '1rem', color: 'var(--text-secondary)' }}>Thumbnail</h4>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', alignItems: 'flex-start' }}>
                                <img
                                    src={post.thumbnail}
                                    alt="Thumbnail"
                                    style={{ width: '240px', height: 'auto', borderRadius: '8px', objectFit: 'cover' }}
                                />
                                <div style={{ display: 'flex', gap: '0.5rem', width: '240px' }}>
                                    <button className="btn btn-secondary btn-sm" onClick={handleDownloadThumbnail} style={{ flex: 1, justifyContent: 'center' }}>
                                        ⬇️ Download
                                    </button>
                                    <button id="copy-thumb-btn" className="btn btn-secondary btn-sm" onClick={handleCopyImage} style={{ flex: 1, justifyContent: 'center' }}>
                                        {isThumbnailCopied ? '✅ COPIED' : '📋 Copy Image'}
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div className="card" style={{ padding: '1.5rem' }}>
                            <h4 style={{ marginBottom: '1rem', fontSize: '1rem', color: 'var(--text-secondary)' }}>Reference URL</h4>
                            <div className="input-group" style={{ marginBottom: '0' }}>
                                <div style={{ display: 'flex', gap: '0.5rem' }}>
                                    <input
                                        type="text"
                                        className="input-field"
                                        value={post.url}
                                        readOnly
                                        style={{ flex: 1, fontSize: '0.9rem' }}
                                    />
                                    <button className="btn btn-primary" onClick={handleCopyUrl}>
                                        🔗 {copyUrlText}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Additional Info */}
                    <div className="card" style={{ padding: '2rem', marginTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
                        {isEditing ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                                <div className="input-group">
                                    <label className="input-label">Title</label>
                                    <input
                                        type="text"
                                        className="input-field"
                                        value={editedTitle}
                                        onChange={e => setEditedTitle(e.target.value)}
                                    />
                                </div>
                                <div className="input-group">
                                    <label className="input-label">Memo</label>
                                    <textarea
                                        className="input-field"
                                        value={editedMemo}
                                        onChange={e => setEditedMemo(e.target.value)}
                                        rows={4}
                                    />
                                </div>
                                <div className="grid grid-2" style={{ gap: '1rem' }}>
                                    <CategorySelector
                                        categories={categories}
                                        type="primary"
                                        selected={editedPrimary}
                                        onChange={setEditedPrimary}
                                    />
                                    <CategorySelector
                                        categories={categories}
                                        type="secondary"
                                        selected={editedSecondary}
                                        onChange={setEditedSecondary}
                                    />
                                </div>
                                <div className="input-group">
                                    <label className="input-label">Video Type</label>
                                    <div className="flex gap-2">
                                        <button
                                            className={`btn btn-sm ${editedVideoType === 'long' ? 'btn-primary' : 'btn-secondary'}`}
                                            onClick={() => setEditedVideoType('long')}
                                        >
                                            📺 Long Form
                                        </button>
                                        <button
                                            className={`btn btn-sm ${editedVideoType === 'short' ? 'btn-primary' : 'btn-secondary'}`}
                                            onClick={() => setEditedVideoType('short')}
                                        >
                                            📱 Short Form
                                        </button>
                                    </div>
                                </div>
                                <div className="flex gap-2 mt-4">
                                    <button className="btn btn-primary flex-1" onClick={handleUpdate} disabled={isSaving}>
                                        {isSaving ? 'Saving...' : '💾 Save Changes'}
                                    </button>
                                    <button className="btn btn-secondary" onClick={() => setIsEditing(false)}>
                                        ❌ Cancel
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                                    <div>
                                        <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{post.title}</h2>
                                    </div>
                                    <div className="flex gap-2">
                                        {currentUser && (currentUser.is_admin || currentUser.id === post.user_id) && (
                                            <>
                                                <button className="btn btn-secondary btn-sm" onClick={() => setIsEditing(true)}>
                                                    ✏️ Edit
                                                </button>
                                                <button className="btn btn-danger btn-sm" onClick={handleDelete}>
                                                    🗑️ Delete
                                                </button>
                                            </>
                                        )}
                                    </div>
                                </div>
                                <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
                                    {post.memo || 'No memo provided.'}
                                </p>
                                <div style={{ marginTop: '2rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                                    Added by {post.author_name || 'Unknown'} on {new Date(post.created_at).toLocaleDateString()}
                                </div>
                            </div>
                        )}
                    </div>

                </div>
            </div>
        </div>
    );

    if (isModal) {
        return (
            <div className="modal-overlay" onClick={onClose}>
                {content}
            </div>
        );
    }

    return content;
}
