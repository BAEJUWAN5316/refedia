import React, { useState } from 'react';
import CategorySelector from './CategorySelector';

import { API_URL } from '../config';

export default function PostCreate({ onClose, onPostCreated }) {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [categories, setCategories] = useState({ primary: [], secondary: [] });

    // Form State
    const [primaryCats, setPrimaryCats] = useState([]);
    const [secondaryCats, setSecondaryCats] = useState([]);
    const [memo, setMemo] = useState('');

    // Fetch categories on mount
    React.useEffect(() => {
        fetchCategories();
    }, []);

    const fetchCategories = async () => {
        try {
            const response = await fetch(`${API_URL}/api/categories`);
            const data = await response.json();
            setCategories(data);
        } catch (err) {
            console.error('Failed to fetch categories:', err);
        }
    };

    const handleSubmit = async () => {
        if (!url) {
            setError('Please enter a YouTube URL');
            return;
        }

        // Basic validation
        if (!url.includes('youtube.com/') && !url.includes('youtu.be/')) {
            setError('Please enter a valid YouTube URL');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const token = sessionStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/posts`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    url,
                    primary_categories: primaryCats,
                    secondary_categories: secondaryCats,
                    memo
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to create post');
            }

            onPostCreated();
            onClose();
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" style={{ maxWidth: '600px', width: '90%' }} onClick={(e) => e.stopPropagation()}>
                <div className="modal-header" style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)' }}>
                    <h3 className="modal-title" style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>New Reference</h3>
                    <button className="btn btn-icon" onClick={onClose} style={{ fontSize: '1.2rem' }}>❌</button>
                </div>

                <div className="modal-body" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    {error && (
                        <div className="text-danger" style={{ padding: '0.75rem', background: '#ffebee', borderRadius: '8px', border: '1px solid #ffcdd2' }}>
                            {error}
                        </div>
                    )}

                    <div className="input-group">
                        <label className="input-label" style={{ fontSize: '1rem', marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>
                            YouTube URL <span style={{ color: 'red' }}>*</span>
                        </label>
                        <input
                            type="text"
                            className="input-field"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            placeholder="https://www.youtube.com/watch?v=..."
                            autoFocus
                            style={{ padding: '0.75rem', fontSize: '1rem', width: '100%' }}
                        />
                    </div>

                    <div className="grid grid-2" style={{ gap: '1.5rem' }}>
                        <div className="input-group">
                            <label className="input-label" style={{ fontSize: '1rem', marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>
                                Primary Category
                            </label>
                            <CategorySelector
                                categories={categories}
                                type="primary"
                                selected={primaryCats}
                                onChange={setPrimaryCats}
                                maxSelect={1}
                            />
                        </div>

                        <div className="input-group">
                            <label className="input-label" style={{ fontSize: '1rem', marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>
                                Secondary Category
                            </label>
                            <CategorySelector
                                categories={categories}
                                type="secondary"
                                selected={secondaryCats}
                                onChange={setSecondaryCats}
                                maxSelect={1}
                            />
                        </div>
                    </div>

                    <div className="input-group">
                        <label className="input-label" style={{ fontSize: '1rem', marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>
                            Memo
                        </label>
                        <textarea
                            className="input-field"
                            rows={4}
                            value={memo}
                            onChange={(e) => setMemo(e.target.value)}
                            placeholder="Add a note about this reference..."
                            style={{ padding: '0.75rem', fontSize: '1rem', width: '100%', resize: 'vertical' }}
                        />
                    </div>

                    <div className="flex gap-3 mt-4" style={{ paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
                        <button
                            className="btn btn-primary"
                            onClick={handleSubmit}
                            disabled={loading}
                            style={{ flex: 2, padding: '0.75rem', fontSize: '1.1rem', justifyContent: 'center' }}
                        >
                            {loading ? '💾 Saving...' : '💾 Save Reference'}
                        </button>
                        <button
                            className="btn btn-secondary"
                            onClick={onClose}
                            style={{ flex: 1, padding: '0.75rem', fontSize: '1.1rem', justifyContent: 'center' }}
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
