import React from 'react';
import SearchBar from './SearchBar';

export default function Header({
    onSearch,
    onAdminClick,
    currentUser,
    onLoginClick,
    onLogoutClick,
    onCreateClick
}) {
    return (
        <header className="header">
            <div className="container header-content">
                <div className="logo-section">
                    <h1 className="logo">Refedia</h1>
                </div>

                {currentUser && (
                    <div className="search-section">
                        <SearchBar onSearch={onSearch} />
                    </div>
                )}

                <div className="actions-section">
                    {currentUser ? (
                        <div className="user-menu">
                            <button className="btn btn-primary" onClick={onCreateClick}>
                                ➕ New Reference
                            </button>

                            {currentUser.is_admin && (
                                <button className="btn btn-secondary" onClick={onAdminClick} title="Admin Dashboard">
                                    ⚙️ Admin
                                </button>
                            )}

                            <div className="user-info">
                                <span className="user-name">👤 {currentUser.name}</span>
                                <button className="btn btn-sm btn-secondary" onClick={onLogoutClick}>
                                    Logout
                                </button>
                            </div>
                        </div>
                    ) : (
                        <button className="btn btn-primary" onClick={onLoginClick}>
                            Login
                        </button>
                    )}
                </div>
            </div>
        </header>
    );
}
