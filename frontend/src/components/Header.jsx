import React from 'react';
import SearchBar from './SearchBar';
import refediaLogo from '../../assets/refedia.png';

export default function Header({
    onSearch,
    onAdminClick,
    onCreateClick,
    currentUser,
    onLoginClick,
    onLogoutClick
}) {
    return (
        <header className="header">
            <div className="container header-content">
                <div className="logo-section">
                    <img src={refediaLogo} alt="Refedia" style={{ width: '150px', height: 'auto' }} />
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
                                + New Reference
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
