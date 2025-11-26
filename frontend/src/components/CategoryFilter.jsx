import React from 'react';

export default function CategoryFilter({
    categories,
    selectedPrimary,
    onSelectPrimary,
    selectedSecondary,
    onSelectSecondary,
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
                </div>
            </div>

            {/* Primary Categories */}
            <div style={{ width: '100%' }}>
                <h5 style={{ marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Primary Categories</h5>
                <div className="filter-group" style={{ flexWrap: 'wrap' }}>
                    <button
                        className={`btn ${selectedPrimary.length === 0 ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => onSelectPrimary([])}
                    >
                        All
                    </button>
                    {categories.primary.map(cat => (
                        <button
                            key={cat.id}
                            className={`btn ${selectedPrimary.includes(cat.id) ? 'btn-primary' : 'btn-secondary'}`}
                            onClick={() => toggleSelection(cat.id, selectedPrimary, onSelectPrimary)}
                        >
                            {cat.name}
                        </button>
                    ))}
                </div>
            </div>

            {/* Secondary Categories */}
            <div style={{ width: '100%' }}>
                <h5 style={{ marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Secondary Categories</h5>
                <div className="filter-group" style={{ flexWrap: 'wrap' }}>
                    <button
                        className={`btn ${selectedSecondary.length === 0 ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => onSelectSecondary([])}
                    >
                        All
                    </button>
                    {categories.secondary.map(cat => (
                        <button
                            key={cat.id}
                            className={`btn ${selectedSecondary.includes(cat.id) ? 'btn-primary' : 'btn-secondary'}`}
                            onClick={() => toggleSelection(cat.id, selectedSecondary, onSelectSecondary)}
                        >
                            {cat.name}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}
