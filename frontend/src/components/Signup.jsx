import { useState } from 'react';
import '../auth.css';

import { API_URL } from '../config';

export default function Signup({ onSwitchToLogin }) {
    const [email, setEmail] = useState('');
    const [name, setName] = useState('');
    const [employeeId, setEmployeeId] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await fetch(`${API_URL}/api/auth/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email,
                    name,
                    employee_id: employeeId
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Signup failed');
            }

            alert('Account created! Please login.');
            onSwitchToLogin();
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2 className="auth-title">Create Account</h2>

                {error && <div className="auth-error">{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="input-group">
                        <label className="input-label">Email</label>
                        <input
                            type="email"
                            className="input-field"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>

                    <div className="input-group">
                        <label className="input-label">Name</label>
                        <input
                            type="text"
                            className="input-field"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            required
                        />
                    </div>

                    <div className="input-group">
                        <label className="input-label">Employee ID (사번)</label>
                        <input
                            type="text"
                            className="input-field"
                            value={employeeId}
                            onChange={(e) => setEmployeeId(e.target.value)}
                            required
                        />
                    </div>

                    <button type="submit" className="btn btn-primary auth-btn" disabled={loading}>
                        {loading ? 'Creating account...' : 'Sign Up'}
                    </button>
                </form>

                <div className="auth-toggle">
                    Already have an account?{' '}
                    <button onClick={onSwitchToLogin}>Login</button>
                </div>
            </div>
        </div>
    );
}
