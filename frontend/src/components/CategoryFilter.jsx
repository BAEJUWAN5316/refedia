import React from 'react';

export default function CategoryFilter({
    categories,
    selectedIndustry, onSelectIndustry,
    selectedGenre, onSelectGenre,
    selectedCast, onSelectCast,
    selectedMood, onSelectMood,
    selectedEditing, onSelectEditing,
    filterLogic,
    onToggleLogic,
    selectedVideoType,
    onSelectVideoType,
    ...props
}) {
    const toggleSelection = (id, currentSelected, setSelection) => {
        if (currentSelected.includes(id)) {
            setSelection(currentSelected.filter(item => item !== id));
        } else {
            setSelection([...currentSelected, id]);
        }
    };

    const renderCategoryGroup = (title, list, selected, onSelect) => (
        <div style={{ width: '100%' }}>
            <h5 style={{ marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>{title}</h5>
            <div className="filter-group" style={{ flexWrap: 'wrap' }}>
                <button
                    className={`btn ${selected.length === 0 ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => onSelect([])}
                >
                    All
                </button>
                {list && list.map(cat => (
                    <button
                        key={cat.id}
                        className={`btn ${selected.includes(cat.id) ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => toggleSelection(cat.id, selected, onSelect)}
                    >
                        {cat.name}
                    </button>
                ))}
            </div>
        </div>
    );

    return (
        <div className="filter-section" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '1rem' }}>
            {/* Logic Toggle & Video Type */}
            <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                <div className="filter-group">
                    <button
                        className={`btn ${selectedVideoType === 'all' ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => onSelectVideoType('all')}
                    >
                        All Types
                    </button>
                    <button
                        className={`btn ${selectedVideoType === 'long' ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => onSelectVideoType('long')}
                    >
                        📺 Long Form
                    </button>
                    <button
                        className={`btn ${selectedVideoType === 'short' ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => onSelectVideoType('short')}
                    >
                        📱 Short Form
                    </button>
                </div>

                <div className="filter-group">
                    <span style={{ marginRight: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Filter Logic:</span>
                    <button
                        className={`btn btn-sm ${filterLogic === 'AND' ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => onToggleLogic('AND')}
                    >
                        AND
                    </button>
                    <button
                        className={`btn btn-sm ${filterLogic === 'OR' ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => onToggleLogic('OR')}
                    >
                        OR
                    </button>
                    <button
                        className="btn btn-sm btn-secondary"
                        onClick={props.onMix}
                        style={{ marginLeft: '0.5rem' }}
                        title="Shuffle Posts"
                    >
                        🔀 Mix
                    </button>
                    <button
                        className="btn btn-sm btn-secondary"
                        onClick={props.onResetSort}
                        style={{ marginLeft: '0.5rem' }}
                        title="Sort by Date"
                    >
                        🕒 Latest
                    </button>
                </div>
            </div>

            {/* Date Range Filter */}
            <div style={{ width: '100%', display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '1rem' }}>
                <div className="filter-group" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Date Range:</span>
                    <input
                        type="date"
                        className="form-input"
                        style={{ padding: '0.4rem', fontSize: '0.9rem', width: 'auto' }}
                        value={props.startDate || ''}
                        onChange={(e) => props.onStartDateChange(e.target.value)}
                    />
                    <span style={{ color: 'var(--text-secondary)' }}>~</span>
                    <input
                        type="date"
                        className="form-input"
                        style={{ padding: '0.4rem', fontSize: '0.9rem', width: 'auto' }}
                        value={props.endDate || ''}
                        onChange={(e) => props.onEndDateChange(e.target.value)}
                    />
                    <button
                        className="btn btn-sm btn-secondary"
                        onClick={() => {
                            props.onStartDateChange('');
                            props.onEndDateChange('');
                        }}
                        style={{ marginLeft: '0.5rem' }}
                    >
                        RESET
                    </button>
                </div>
            </div>

            {renderCategoryGroup("업1종 (Industry)", categories.industry, selectedIndustry, onSelectIndustry)}
            {renderCategoryGroup("장르 (Genre)", categories.genre, selectedGenre, onSelectGenre)}
            {renderCategoryGroup("출연자 (Cast)", categories.cast, selectedCast, onSelectCast)}
            {renderCategoryGroup("분위기 (Mood)", categories.mood, selectedMood, onSelectMood)}
            {renderCategoryGroup("편집/효과 (Editing)", categories.editing, selectedEditing, onSelectEditing)}
        </div>
    );
}
