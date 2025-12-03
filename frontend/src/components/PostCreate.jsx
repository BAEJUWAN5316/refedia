import React, { useState } from 'react';
import CategorySelector from './CategorySelector';

import { API_URL } from '../config';

export default function PostCreate({ onClose, onPostCreated }) {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [categories, setCategories] = useState({
        industry: [], genre: [], cast: [], mood: [], editing: []
    });

    // Form State
    const [industryCats, setIndustryCats] = useState([]);
    const [genreCats, setGenreCats] = useState([]);
    const [castCats, setCastCats] = useState([]);
    const [moodCats, setMoodCats] = useState([]);
    const [editingCats, setEditingCats] = useState([]);

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

    const [analyzing, setAnalyzing] = useState(false);

    const handleAIAnalyze = async () => {
        if (!url) return;

        // Basic validation
        if (!url.includes('youtube.com/') && !url.includes('youtu.be/')) {
            setError('Please enter a valid YouTube URL');
            return;
        }

        setAnalyzing(true);
        setError('');

        try {
            const token = localStorage.getItem('token');

            // 3분 타임아웃 설정
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 180000); // 180초 (3분)

            const response = await fetch(`${API_URL}/api/ai/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ url }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            const data = await response.json();

            if (!response.ok) {
                if (response.status === 429) {
                    throw new Error('AI 추천 기능은 잠시 후 이용해주세요 (사용량 초과)');
                }
                throw new Error(data.detail || 'AI analysis failed');
            }

            // Apply recommended categories
            if (data.industry) setIndustryCats(data.industry);
            if (data.genre) setGenreCats(data.genre);
            if (data.cast) setCastCats(data.cast);
            if (data.mood) setMoodCats(data.mood);
            if (data.editing) setEditingCats(data.editing);

            alert('추천완료!');

        } catch (err) {
            if (err.name === 'AbortError') {
                setError('AI 분석 시간이 초과되었습니다. (서버 응답 없음)');
            } else {
                setError(err.message);
            }
        } finally {
            setAnalyzing(false);
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

        // Category validation
        if (industryCats.length === 0) {
            setError('Please select at least one Industry category');
            return;
        }
        if (genreCats.length === 0) {
            setError('Please select at least one Genre category');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/posts`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    url,
                    industry_categories: industryCats,
                    genre_categories: genreCats,
                    cast_categories: castCats,
                    mood_categories: moodCats,
                    editing_categories: editingCats,
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
            <div className="modal" style={{ maxWidth: '1040px', width: '90%' }} onClick={(e) => e.stopPropagation()}>
                <div className="modal-header" style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h3 className="modal-title" style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>New Reference</h3>
                    <button className="btn btn-icon" onClick={onClose} style={{ fontSize: '1.2rem' }}>❌</button>
                </div>

                <div className="modal-body" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    {error && (
                        <div style={{ padding: '0.75rem', background: '#d32f2f', color: 'white', borderRadius: '8px', fontWeight: 'bold' }}>
                            {error}
                        </div>
                    )}

                    <div className="input-group">
                        <label className="input-label" style={{ fontSize: '1rem', marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>
                            YouTube URL <span style={{ color: 'red' }}>*</span>
                        </label>
                        <div style={{ display: 'flex', gap: '10px' }}>
                            <input
                                type="text"
                                className="input-field"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                placeholder="https://www.youtube.com/watch?v=..."
                                autoFocus
                                style={{ padding: '0.75rem', fontSize: '1rem', width: '100%', flex: 1 }}
                            />
                            <button
                                className="btn btn-secondary"
                                onClick={handleAIAnalyze}
                                disabled={analyzing || !url}
                                style={{ whiteSpace: 'nowrap', minWidth: '120px' }}
                            >
                                {analyzing ? 'AI 분석 중...' : '✨ AI 추천'}
                            </button>
                        </div>
                        {analyzing && (
                            <div style={{ marginTop: '0.5rem', color: '#666', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <span>⏳</span>
                                <span>AI 분석에는 약 1~2분이 소요됩니다. 잠시만 기다려주세요. (영상 길이에 따라 다를 수 있으며 가끔 실패할 수 있습니다...)</span>
                            </div>
                        )}
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                        <div className="input-group">
                            <label className="input-label" style={{ fontSize: '1rem', marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>
                                업종 (Industry) <span style={{ color: 'red' }}>*</span>
                            </label>
                            <CategorySelector
                                categories={categories}
                                type="industry"
                                selected={industryCats}
                                onChange={setIndustryCats}
                            />
                        </div>

                        <div className="input-group">
                            <label className="input-label" style={{ fontSize: '1rem', marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>
                                장르 (Genre) <span style={{ color: 'red' }}>*</span>
                            </label>
                            <CategorySelector
                                categories={categories}
                                type="genre"
                                selected={genreCats}
                                onChange={setGenreCats}
                            />
                        </div>

                        <div className="input-group">
                            <label className="input-label" style={{ fontSize: '1rem', marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>
                                출연자 (Cast)
                            </label>
                            <CategorySelector
                                categories={categories}
                                type="cast"
                                selected={castCats}
                                onChange={setCastCats}
                            />
                        </div>

                        <div className="input-group">
                            <label className="input-label" style={{ fontSize: '1rem', marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>
                                분위기 (Mood)
                            </label>
                            <CategorySelector
                                categories={categories}
                                type="mood"
                                selected={moodCats}
                                onChange={setMoodCats}
                            />
                        </div>

                        <div className="input-group">
                            <label className="input-label" style={{ fontSize: '1rem', marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>
                                편집/효과 (Editing)
                            </label>
                            <CategorySelector
                                categories={categories}
                                type="editing"
                                selected={editingCats}
                                onChange={setEditingCats}
                            />
                        </div>
                    </div>

                    <div className="input-group">
                        <label className="input-label" style={{ fontSize: '1rem', marginBottom: '0.5rem', display: 'block', fontWeight: '500' }}>
                            Memo - 브랜드, 출연자, 장소 등 검색 될 내용을 작성해주세요.
                        </label>
                        <textarea
                            className="input-field"
                            rows={4}
                            value={memo}
                            onChange={(e) => setMemo(e.target.value)}
                            placeholder="EX) 숏박스, 김원훈, 조진세, 서울, 마곡 등..."
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
