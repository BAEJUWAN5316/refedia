import { useState } from 'react';
import '../auth.css';

import { API_URL } from '../config';

export default function Login({ onLogin, onSwitchToSignup }) {
    const [email, setEmail] = useState('');
    const [employeeId, setEmployeeId] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await fetch(`${API_URL}/api/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email,
                    employee_id: employeeId
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Login failed');
            }

            onLogin(data.user, data.access_token);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2 className="auth-title">Login</h2>

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
                        {loading ? 'Logging in...' : 'Login'}
                    </button>
                </form>

                <div className="auth-toggle">
                    Don't have an account?{' '}
                    <button onClick={onSwitchToSignup}>Sign up</button>
                </div>
            </div>
        </div>
    );
}
