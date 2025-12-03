import React, { useState, useEffect } from 'react';

import { API_URL } from '../config';

export default function AdminDashboard({ onClose, categories, onCategoriesChanged, currentUser }) {
    const [users, setUsers] = useState([]);
    const [newCategory, setNewCategory] = useState('');
    const [newCategoryType, setNewCategoryType] = useState('industry');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/admin/users`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setUsers(data);
            }
        } catch (error) {
            console.error('Failed to fetch users:', error);
        }
    };

    const approveUser = async (userId) => {
        if (!confirm('Grant admin privileges to this user?')) return; // Note: The message says "Grant admin privileges" but this is just approval. I should fix the message too.
        // Actually, let's fix the message in a separate step or just ignore it for now as it's minor. 
        // Wait, "Grant admin privileges" for approval is confusing. Let's change it to "Approve this user?".
        if (!confirm('Approve this user?')) return;
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/admin/users/${userId}/approve`, {
                method: 'PUT',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) fetchUsers();
        } catch (error) {
            console.error('Failed to approve user:', error);
        }
    };

    const makeAdmin = async (userId) => {
        if (!confirm('Promote this user to Admin?')) return;
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/admin/users/${userId}/make-admin`, {
                method: 'PUT',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) fetchUsers();
        } catch (error) {
            console.error('Failed to make admin:', error);
        }
    };

    const revokeAdmin = async (userId) => {
        if (!confirm('Revoke admin privileges from this user?')) return;
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/admin/users/${userId}/revoke-admin`, {
                method: 'PUT',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) fetchUsers();
        } catch (error) {
            console.error('Failed to revoke admin:', error);
        }
    };

    const deleteUser = async (userId) => {
        if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) return;
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/admin/users/${userId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) fetchUsers();
        } catch (error) {
            console.error('Failed to delete user:', error);
        }
    };

    const addCategory = async (e) => {
        e.preventDefault();
        if (!newCategory.trim()) return;

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/categories`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    name: newCategory,
                    type: newCategoryType
                })
            });

            if (response.ok) {
                setNewCategory('');
                onCategoriesChanged();
            } else {
                const data = await response.json();
                alert(`Failed to add category: ${data.detail || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Failed to add category:', error);
            alert('Error adding category. See console for details.');
        }
    };

    const deleteCategory = async (categoryId) => {
        if (!confirm('Delete this category?')) return;
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/categories/${categoryId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) onCategoriesChanged();
        } catch (error) {
            console.error('Failed to delete category:', error);
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal" style={{ maxWidth: '800px' }}>
                <div className="modal-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h3 className="modal-title">⚙️ Admin Dashboard</h3>
                    <button className="btn btn-sm btn-secondary" onClick={onClose}>
                        Close
                    </button>
                </div>

                <div className="modal-body">
                    {/* System Management */}
                    <section style={{ marginBottom: '3rem' }}>
                        <h4 style={{ marginBottom: '1rem' }}>🛠️ System Management</h4>
                        <div style={{ display: 'flex', gap: '1rem' }}>
                            <button
                                className="btn btn-primary"
                                onClick={async () => {
                                    if (!confirm('Update view counts for ALL posts? This may take a while.')) return;
                                    try {
                                        const token = localStorage.getItem('token');
                                        const response = await fetch(`${API_URL}/api/admin/update-views`, {
                                            method: 'POST',
                                            headers: { 'Authorization': `Bearer ${token}` }
                                        });
                                        if (response.ok) {
                                            const data = await response.json();
                                            alert(`Success! Updated ${data.updated_count} posts.`);
                                        } else {
                                            alert('Failed to update views.');
                                        }
                                    } catch (error) {
                                        console.error('Failed to update views:', error);
                                        alert('Error updating views.');
                                    }
                                }}
                            >
                                🔄 Update All View Counts
                            </button>
                        </div>
                    </section>

                    {/* User Management */}
                    <section style={{ marginBottom: '3rem' }}>
                        <h4 style={{ marginBottom: '1rem' }}>👥 User Management</h4>
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                <thead>
                                    <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}>
                                        <th style={{ padding: '0.5rem' }}>Name</th>
                                        <th style={{ padding: '0.5rem' }}>Email</th>
                                        <th style={{ padding: '0.5rem' }}>Status</th>
                                        <th style={{ padding: '0.5rem', textAlign: 'right' }}>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {users.map(user => (
                                        <tr key={user.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                                            <td style={{ padding: '0.5rem' }}>{user.name}</td>
                                            <td style={{ padding: '0.5rem' }}>{user.email}</td>
                                            <td style={{ padding: '0.5rem' }}>
                                                {user.is_admin ? (
                                                    <span className="badge badge-primary">ADMIN</span>
                                                ) : user.is_approved ? (
                                                    <span className="badge badge-success">APPROVED</span>
                                                ) : (
                                                    <span className="badge badge-secondary">PENDING</span>
                                                )}
                                            </td>
                                            <td style={{ padding: '0.5rem', textAlign: 'right', display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                                                {!user.is_admin && !user.is_approved && (
                                                    <button className="btn btn-sm btn-primary" onClick={() => approveUser(user.id)}>
                                                        Approve
                                                    </button>
                                                )}
                                                {!user.is_admin && user.is_approved && (
                                                    <button className="btn btn-sm btn-secondary" onClick={() => makeAdmin(user.id)}>
                                                        Make Admin
                                                    </button>
                                                )}
                                                {user.is_admin && user.id !== currentUser?.id && (
                                                    <button className="btn btn-sm btn-danger" onClick={() => revokeAdmin(user.id)}>
                                                        🚫 Revoke Admin
                                                    </button>
                                                )}
                                                {user.id !== currentUser?.id && (
                                                    <button className="btn btn-sm btn-danger" onClick={() => deleteUser(user.id)}>
                                                        🗑️
                                                    </button>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </section>

                    {/* Category Management */}
                    <section>
                        <h4 style={{ marginBottom: '1rem' }}>🏷️ Category Management</h4>

                        <form onSubmit={addCategory} style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
                            <input
                                type="text"
                                className="input-field"
                                placeholder="e.g., Marketing, Video"
                                value={newCategory}
                                onChange={(e) => setNewCategory(e.target.value)}
                                style={{ flex: 1 }}
                            />
                            <select
                                className="input-field"
                                value={newCategoryType}
                                onChange={(e) => setNewCategoryType(e.target.value)}
                                style={{ width: 'auto' }}
                            >
                                <option value="industry">Industry (업종)</option>
                                <option value="genre">Genre (장르)</option>
                                <option value="cast">Cast (출연자)</option>
                                <option value="mood">Mood (분위기)</option>
                                <option value="editing">Editing (편집/효과)</option>
                            </select>
                            <button type="submit" className="btn btn-primary">
                                ➕ Add
                            </button>
                        </form>

                        <div className="grid grid-2" style={{ gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
                            {[
                                { key: 'industry', label: 'Industry (업종)' },
                                { key: 'genre', label: 'Genre (장르)' },
                                { key: 'cast', label: 'Cast (출연자)' },
                                { key: 'mood', label: 'Mood (분위기)' },
                                { key: 'editing', label: 'Editing (편집/효과)' }
                            ].map(type => (
                                <div key={type.key}>
                                    <h5 style={{ marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>{type.label}</h5>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                        {categories[type.key] && categories[type.key].map(cat => (
                                            <div key={cat.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem', background: 'var(--bg-card)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                                                <span>{cat.name}</span>
                                                <button className="btn btn-sm btn-danger" onClick={() => deleteCategory(cat.id)}>
                                                    🗑️
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>
                </div>
            </div>
        </div>
    );
}
