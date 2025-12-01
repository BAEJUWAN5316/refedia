import { Link } from 'react-router-dom';
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
                    {currentUser ? (
                        <div className="user-menu-wrapper">
                            <div className="user-menu-top">
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
