import React from 'react';

export default function SearchBar({ onSearch }) {
    return (
        <div className="search-bar">
            <span className="search-icon">🔍</span>
            <input 
                type="text" 
                placeholder="Search references..." 
                onChange={(e) => onSearch(e.target.value)}
                className="search-input"
            />
        </div>
    );
}
