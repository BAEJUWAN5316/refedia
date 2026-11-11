export default function CategorySelector({ categories, selected, onChange, type, collapsible = true }) {
    const Container = collapsible ? 'details' : 'div';
    const Label = collapsible ? 'summary' : 'p';
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
        <Container className="category-selector" open={collapsible && selected.length > 0 ? true : undefined}>
            <Label className="input-label">
                {selected.length ? `${selected.length}개 선택됨` : getLabel()}
            </Label>
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
                            style={{ width: '14px', height: '14px', accentColor: 'var(--accent-primary)' }}
                        />
                        {cat.name}
                    </label>
                ))}
            </div>
        </Container>
    );
}
