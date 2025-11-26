import React, { useState, useEffect } from 'react';
import CategorySelector from './CategorySelector';

const API_URL = 'http://localhost:8000';

export default function PostDetail({ postId, currentUser, onClose, onUpdate }) {
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
    const [loadingFrames, setLoadingFrames] = useState(false);
    const [frames, setFrames] = useState([]);
    const [copyUrlText, setCopyUrlText] = useState('Copy');
    const [isSaving, setIsSaving] = useState(false);
    const [isThumbnailCopied, setIsThumbnailCopied] = useState(false);
    const [copiedFrameIdx, setCopiedFrameIdx] = useState(null);

    useEffect(() => {
        fetchPost();
        fetchCategories();
    }, [postId]);

    const fetchPost = async () => {
        try {
            const token = sessionStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/posts/${postId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!response.ok) throw new Error('Failed to fetch post');
            const data = await response.json();
            setPost(data);
            setEditedTitle(data.title);
            setEditedMemo(data.memo || '');
            setEditedPrimary(data.primary_categories || (data.primary_category_id ? [data.primary_category_id] : []));
            setEditedSecondary(data.secondary_categories || (data.secondary_category_id ? [data.secondary_category_id] : []));
            setEditedVideoType(data.video_type);
            setFrames(data.frames || []);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const fetchCategories = async () => {
        try {
            const token = sessionStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/categories`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setCategories(data);
            }
        } catch (error) {
            console.error('Failed to fetch categories:', error);
        }
    };

    const handleDownloadImage = async (imageUrl, filename) => {
        try {
            let blob;
            if (imageUrl.startsWith('data:')) {
                // Handle Base64
                const response = await fetch(imageUrl);
                blob = await response.blob();
            } else {
                // Handle URL via Proxy
                const token = sessionStorage.getItem('token');
                const proxyUrl = `${API_URL}/api/download/image?url=${encodeURIComponent(imageUrl)}`;
                const response = await fetch(proxyUrl, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!response.ok) throw new Error('Download failed');
                blob = await response.blob();
            }

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename || 'download.jpg';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Download error:', error);
            alert('Failed to download image');
        }
    };

    const handleCopyBase64Image = async (base64String, idx) => {
        try {
            const response = await fetch(base64String);
            const blob = await response.blob();
            await navigator.clipboard.write([
                new ClipboardItem({
                    [blob.type]: blob
                })
            ]);
            setCopiedFrameIdx(idx);
            setTimeout(() => setCopiedFrameIdx(null), 2000);
        } catch (err) {
            console.error('Failed to copy image:', err);
            // alert('Failed to copy image to clipboard'); // Alert removed
        }
    };

    const getCategoryName = (categoryId, type) => {
        const list = type === 'primary' ? categories.primary : categories.secondary;
        const category = list.find(c => c.id === categoryId);
        return category ? category.name : categoryId;
    };

    const getYouTubeEmbedUrl = (url) => {
        if (!url) return '';
        let videoId = '';

        // youtube.com/watch?v=VIDEO_ID
        if (url.includes('v=')) {
            videoId = url.split('v=')[1]?.split('&')[0];
        }
        // youtu.be/VIDEO_ID
        else if (url.includes('youtu.be/')) {
            videoId = url.split('youtu.be/')[1]?.split('?')[0];
        }
        // youtube.com/shorts/VIDEO_ID
        else if (url.includes('shorts/')) {
            videoId = url.split('shorts/')[1]?.split('?')[0];
        }

        return videoId ? `https://www.youtube.com/embed/${videoId}` : '';
    };

    const handleRefreshFrames = async () => {
        if (!post?.url) return;
        setLoadingFrames(true);
        try {
            const token = sessionStorage.getItem('token');
            const response = await fetch(
                `${API_URL}/api/youtube/frames?url=${encodeURIComponent(post.url)}&count=4`,
                { headers: { 'Authorization': `Bearer ${token}` } }
            );

            if (response.ok) {
                const data = await response.json();
                const newFrames = data.frames || []; // Backend returns { frames: [...], count: ... }
                setFrames(newFrames);
                // Update local post state with new frames
                setPost(prev => ({ ...prev, frames: newFrames }));

                // Also update backend to save these frames
                await fetch(`${API_URL}/api/posts/${postId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        ...post,
                        frames: newFrames
                    })
                });
            }
        } catch (error) {
            console.error('Failed to refresh frames:', error);
            alert('Failed to refresh frames');
        } finally {
            setLoadingFrames(false);
        }
    };

    const handleCopyUrl = async () => {
        if (post?.url) {
            try {
                await navigator.clipboard.writeText(post.url);
                setCopyUrlText('Copied!');
                setTimeout(() => setCopyUrlText('Copy'), 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        }
    };

    const convertBlobToPng = (blob) => {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                canvas.toBlob((pngBlob) => {
                    resolve(pngBlob);
                }, 'image/png');
            };
            img.onerror = reject;
            img.src = URL.createObjectURL(blob);
        });
    };

    const handleCopyImage = async () => {
        if (!post?.thumbnail) return;
        try {
            let blob;
            if (post.thumbnail.startsWith('data:')) {
                const response = await fetch(post.thumbnail);
                blob = await response.blob();
            } else {
                const token = sessionStorage.getItem('token');
                // Use proxy to avoid CORS
                const proxyUrl = `${API_URL}/api/download/image?url=${encodeURIComponent(post.thumbnail)}`;
                const response = await fetch(proxyUrl, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (!response.ok) throw new Error('Failed to fetch image');
                blob = await response.blob();
            }

            // Try copying directly first
            try {
                await navigator.clipboard.write([
                    new ClipboardItem({
                        [blob.type]: blob
                    })
                ]);
            } catch (writeError) {
                console.warn('Direct copy failed, trying PNG conversion:', writeError);
                // Fallback: Convert to PNG and try again (fixes WebP/unsupported type issues)
                const pngBlob = await convertBlobToPng(blob);
                await navigator.clipboard.write([
                    new ClipboardItem({
                        'image/png': pngBlob
                    })
                ]);
            }

            setIsThumbnailCopied(true);
            setTimeout(() => setIsThumbnailCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy image:', err);
            // Show failure feedback on button
            const btn = document.getElementById('copy-thumb-btn');
            if (btn) {
                const originalText = btn.innerText;
                btn.innerText = '❌ Failed';
                setTimeout(() => btn.innerText = originalText, 2000);
            }
        }
    };

    const handleDownloadThumbnail = () => {
        if (post?.thumbnail) {
            handleDownloadImage(post.thumbnail, `thumbnail-${postId}.jpg`);
        }
    };

    const handleUpdate = async () => {
        setIsSaving(true);
        try {
            const token = sessionStorage.getItem('token');
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
                    video_type: editedVideoType,
                    frames: frames
                })
            });

            if (!response.ok) throw new Error('Failed to update post');

            const updatedPost = await response.json();
            setPost(updatedPost);
            setIsEditing(false);
            if (onUpdate) onUpdate();
        } catch (err) {
            alert(err.message);
        } finally {
            setIsSaving(false);
        }
    };

    const handleDelete = async () => {
        if (!confirm('Are you sure you want to delete this post?')) return;
        try {
            const token = sessionStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/posts/${postId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                onClose();
                if (onUpdate) onUpdate();
            }
        } catch (err) {
            alert('Failed to delete post');
        }
    };

    if (loading) return <div className="loading-container"><div className="spinner"></div></div>;
    if (error) return <div className="text-center text-danger">{error}</div>;
    if (!post) return null;

    const embedUrl = getYouTubeEmbedUrl(post.url);

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" style={{ maxWidth: '1000px', width: '90%', height: '90vh', display: 'flex', flexDirection: 'column', padding: '0' }} onClick={e => e.stopPropagation()}>
                {/* Header */}
                <div className="modal-header" style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                    <div style={{ flex: 1 }}>
                        <h3 className="modal-title" style={{ fontSize: '1.2rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                            {isEditing ? 'Edit Reference' : post.title}
                        </h3>
                        {!isEditing && (
                            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
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
                                <span className={`badge ${post.video_type === 'long' ? 'badge-long' : 'badge-short'}`}>
                                    {post.video_type === 'long' ? '📺 Long Form' : '📱 Short Form'}
                                </span>
                            </div>
                        )}
                    </div>
                    <button className="btn btn-icon" onClick={onClose} style={{ background: 'transparent', border: 'none', fontSize: '1.2rem', cursor: 'pointer', marginLeft: '1rem' }}>
                        ❌
                    </button>
                </div>

                <div className="modal-body" style={{ flex: 1, overflowY: 'auto', padding: '2rem' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>

                        {/* 1. Playable YouTube Screen (Top Priority) */}
                        <div style={{ width: '100%' }}>
                            <div style={{ position: 'relative', paddingTop: '56.25%', background: '#000', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 4px 20px rgba(0,0,0,0.3)' }}>
                                <iframe
                                    src={embedUrl}
                                    style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none' }}
                                    allowFullScreen
                                />
                            </div>
                        </div>

                        {/* 2. Thumbnail & 3. URL (Side by Side or Stacked) */}
                        <div className="grid grid-2" style={{ gap: '1.5rem', alignItems: 'start' }}>
                            {/* 2. Thumbnail Display & Actions */}
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

                        {/* 4. Frame Extraction */}
                        <div className="card" style={{ padding: '1.5rem' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                <h4 style={{ margin: 0, fontSize: '1.1rem' }}>Key Frames</h4>
                                <button
                                    className="btn btn-secondary btn-sm"
                                    onClick={handleRefreshFrames}
                                    disabled={loadingFrames}
                                >
                                    {loadingFrames ? '🔄 Extracting...' : '🔄 Extract New Frames'}
                                </button>
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem' }}>
                                {frames.map((frame, idx) => (
                                    <div key={idx} style={{ position: 'relative', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
                                        <img
                                            src={frame}
                                            alt={`Frame ${idx + 1}`}
                                            style={{ width: '100%', height: 'auto', display: 'block' }}
                                        />
                                        <div style={{
                                            position: 'absolute',
                                            top: 0, left: 0, right: 0, bottom: 0,
                                            background: 'rgba(0,0,0,0.6)',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            opacity: 0,
                                            transition: 'opacity 0.2s',
                                            cursor: 'pointer'
                                        }}
                                            onMouseEnter={e => e.currentTarget.style.opacity = 1}
                                            onMouseLeave={e => e.currentTarget.style.opacity = 0}
                                            onClick={() => handleDownloadImage(frame, `frame-${idx + 1}.jpg`)}
                                        >
                                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                <button
                                                    className="btn btn-sm btn-primary"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleDownloadImage(frame, `frame-${idx + 1}.jpg`);
                                                    }}
                                                >
                                                    ⬇️
                                                </button>
                                                <button
                                                    className={`btn btn-sm ${copiedFrameIdx === idx ? 'btn-success' : 'btn-secondary'}`}
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleCopyBase64Image(frame, idx);
                                                    }}
                                                    style={{
                                                        backgroundColor: copiedFrameIdx === idx ? '#28a745' : '',
                                                        color: copiedFrameIdx === idx ? 'white' : ''
                                                    }}
                                                >
                                                    {copiedFrameIdx === idx ? '✅' : '📋'}
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                                {frames.length === 0 && (
                                    <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                                        No frames extracted yet. Click the button above to extract.
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Additional Info (Title, Desc, Categories, Edit) */}
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
        </div>
    );
}
