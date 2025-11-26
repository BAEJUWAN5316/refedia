export default function CategorySelector({ categories, selected, onChange, type }) {
    const categoryList = type === 'primary' ? categories.primary : categories.secondary;

    const toggleCategory = (categoryId) => {
        if (selected.includes(categoryId)) {
            onChange(selected.filter(id => id !== categoryId));
        } else {
            onChange([...selected, categoryId]);
        }
    };

    return (
        <div className="input-group">
            <label className="input-label">
                {type === 'primary' ? 'Primary Categories' : 'Secondary Categories'}
                <span style={{ color: 'var(--error)' }}> *</span>
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
