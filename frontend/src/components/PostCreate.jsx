import React, { useState } from 'react';
import CategorySelector from './CategorySelector';

const API_URL = 'http://localhost:8000';

export default function PostCreate({ onClose, onPostCreated }) {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [step, setStep] = useState(1); // 1: URL Input, 2: Details
    const [metadata, setMetadata] = useState(null);
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

    const handleUrlSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            // Validate URL format first
            if (!url.includes('youtube.com/') && !url.includes('youtu.be/')) {
                throw new Error('Please enter a valid YouTube URL');
            }

            // In a real app, we might want to pre-validate with backend or just proceed
            // Here we'll just move to next step and let backend handle extraction on save
            // OR we can fetch metadata now. Let's fetch metadata now to show preview.
            // But the backend create_post handles extraction. 
            // Let's just move to step 2 and show the URL. 
            // Ideally we should have an endpoint to "preview" or "extract" metadata before saving.
            // For now, let's assume we just collect data and submit.

            setStep(2);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async () => {
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
        <div className="modal-overlay">
            <div className="modal">
                <div className="modal-header">
                    <h3 className="modal-title">New Reference</h3>
                    <button className="btn btn-icon" onClick={onClose}>❌</button>
                </div>

                <div className="modal-body">
                    {error && <div className="text-danger mb-3">{error}</div>}

                    {step === 1 ? (
                        <div className="input-group">
                            <label className="input-label">YouTube URL</label>
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    className="input-field"
                                    value={url}
                                    onChange={(e) => setUrl(e.target.value)}
                                    placeholder="https://www.youtube.com/watch?v=..."
                                    autoFocus
                                />
                                <button
                                    className="btn btn-primary"
                                    onClick={handleUrlSubmit}
                                    disabled={!url || loading}
                                >
                                    Next
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="flex flex-col gap-3">
                            <div className="input-group">
                                <label className="input-label">URL</label>
                                <input type="text" className="input-field" value={url} disabled />
                            </div>

                            <div className="input-group">
                                <label className="input-label">Primary Category (Max 1)</label>
                                <CategorySelector
                                    categories={categories}
                                    type="primary"
                                    selected={primaryCats}
                                    onChange={setPrimaryCats}
                                    maxSelect={1}
                                />
                            </div>

                            <div className="input-group">
                                <label className="input-label">Secondary Category (Max 1)</label>
                                <CategorySelector
                                    categories={categories}
                                    type="secondary"
                                    selected={secondaryCats}
                                    onChange={setSecondaryCats}
                                    maxSelect={1}
                                />
                            </div>

                            <div className="input-group">
                                <label className="input-label">Memo</label>
                                <textarea
                                    className="input-field"
                                    rows={3}
                                    value={memo}
                                    onChange={(e) => setMemo(e.target.value)}
                                    placeholder="Add a note..."
                                />
                            </div>

                            <div className="flex justify-between mt-4">
                                <button className="btn btn-secondary" onClick={() => setStep(1)}>Back</button>
                                <button
                                    className="btn btn-primary"
                                    onClick={handleSubmit}
                                    disabled={loading}
                                >
                                    {loading ? 'Saving...' : 'Save Reference'}
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
