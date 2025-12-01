export default function CategorySelector({ categories, selected, onChange, type }) {
    // type: 'industry', 'genre', 'cast', 'mood', 'editing'
    const categoryList = categories[type] || [];

    const toggleCategory = (categoryId) => {
        if (selected.includes(categoryId)) {
            onChange(selected.filter(id => id !== categoryId));
        } else {
            onChange([...selected, categoryId]);
        }
    };

    const getLabel = () => {
        switch (type) {
            case 'industry': return '- 필수 항목입니다.';
            case 'genre': return '- 필수 항목입니다.';
            case 'cast': return '- 선택 항목입니다.';
            case 'mood': return '- 선택 항목입니다.';
            case 'editing': return '- 선택 항목입니다.';
            default: return 'Categories';
        }
    };

    return (
        <div className="input-group">
            <label className="input-label">
                {getLabel()}
            </label>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {categoryList.map((cat) => (
                    <label
                        key={cat.id}
                        style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            padding: '0.5rem 1rem',
                            background: selected.includes(cat.id) ? 'var(--accent-primary)' : 'var(--bg-card)',
                            border: `1px solid ${selected.includes(cat.id) ? 'var(--accent-primary)' : 'var(--border-color)'}`,
                            borderRadius: '8px',
                            cursor: 'pointer',
                            transition: 'var(--transition)',
                            color: selected.includes(cat.id) ? 'white' : 'var(--text-primary)'
                        }}
                    >
                        <input
                            type="checkbox"
                            checked={selected.includes(cat.id)}
                            onChange={() => toggleCategory(cat.id)}
                            style={{ display: 'none' }}
                        />
                        {cat.name}
                    </label>
                ))}
            </div>
        </div>
    );
}
