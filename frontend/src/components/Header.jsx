import { Link } from 'react-router-dom';
import { useState } from 'react';
import SearchBar from './SearchBar';
import refediaLogo from '../../assets/refedia.png';

export default function Header({
    onSearch,
    onAdminClick,
    onCreateClick,
    currentUser,
    onLoginClick,
    onLogoutClick,
    viewMode,
    onViewModeChange,
    onLogoClick
}) {
    const [presentation, setPresentation] = useState(() => document.documentElement.dataset.presentation || 'studio');
    const togglePresentation = () => {
        const next = presentation === 'studio' ? 'classic' : 'studio';
        document.documentElement.dataset.presentation = next;
        setPresentation(next);
        try { localStorage.setItem('refedia-presentation', next); } catch { /* Session-only preference */ }
    };
    return (
        <header className="header">
            <div className="container header-content">
                <div className="logo-section">
                    <Link
                        to="/"
                        onClick={onLogoClick}
                        style={{ display: 'block', textDecoration: 'none' }}
                    >
                        <img src={refediaLogo} alt="Refedia" style={{ width: '150px', height: 'auto', display: 'block' }} />
                    </Link>
                </div>

                {currentUser && (
                    <div className="search-section">
                        <SearchBar onSearch={onSearch} />
                    </div>
                )}

                <div className="actions-section">
                    <button type="button" className="presentation-toggle" onClick={togglePresentation}
                        title="화면 스타일 비교" aria-label={presentation === 'studio' ? '기존 화면으로 전환' : '새 화면으로 전환'}>
                        {presentation === 'studio' ? '기존 화면 보기' : '새 화면 보기'}
                    </button>
                    {currentUser ? (
                        <div className="user-menu-wrapper">
                            <div className="user-menu-top">
                                <button className="btn btn-primary" onClick={onCreateClick}>
                                    + New Reference
                                </button>

                                {currentUser.is_admin && (
                                    <button className="btn btn-secondary" onClick={onAdminClick} title="Admin Dashboard">
                                        Admin
                                    </button>
                                )}

                                <div className="user-info">
                                    <span className="user-name">{currentUser.name}</span>
                                    <button className="btn btn-sm btn-secondary" onClick={onLogoutClick}>
                                        Logout
                                    </button>
                                </div>
                            </div>

                            <div className="user-menu-bottom">
                                <div className="nav-pills">
                                    <button
                                        className={`nav-pill ${viewMode === 'all' ? 'active' : ''}`}
                                        onClick={() => onViewModeChange('all')}
                                    >
                                        All Refs
                                    </button>
                                    <button
                                        className={`nav-pill ${viewMode === 'my_posts' ? 'active' : ''}`}
                                        onClick={() => onViewModeChange('my_posts')}
                                    >
                                        My Posts
                                    </button>
                                    <button
                                        className={`nav-pill ${viewMode === 'favorites' ? 'active' : ''}`}
                                        onClick={() => onViewModeChange('favorites')}
                                    >
                                        Favorites
                                    </button>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <button className="btn btn-primary" onClick={onLoginClick}>
                            Login
                        </button>
                    )}
                </div>
            </div >
        </header >
    );
}
