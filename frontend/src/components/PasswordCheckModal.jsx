import React, { useState } from 'react';

const API_URL = 'http://localhost:8000';

export default function PasswordCheckModal({ onSuccess, onClose }) {
    const [employeeId, setEmployeeId] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleVerify = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const token = sessionStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/auth/verify-password`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ employee_id: employeeId })
            });

            if (!response.ok) {
                throw new Error('Verification failed');
            }

            onSuccess();
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal" style={{ maxWidth: '400px' }}>
                <div className="modal-header">
                    <h3 className="modal-title">Admin Verification</h3>
                    <button className="btn btn-sm btn-secondary" onClick={onClose}>
                        Close
                    </button>
                </div>

                <div className="modal-body">
                    {error && <div className="auth-error">{error}</div>}
                    
                    <form onSubmit={handleVerify}>
                        <div className="input-group">
                            <label className="input-label">Employee ID (사번)</label>
                            <input
                                type="text"
                                className="input-field"
                                value={employeeId}
                                onChange={(e) => setEmployeeId(e.target.value)}
                                placeholder="Enter your Employee ID"
                                required
                            />
                        </div>

                        <div className="modal-footer" style={{ padding: 0 }}>
                            <button type="submit" className="btn btn-primary" disabled={loading}>
                                {loading ? 'Verifying...' : 'Verify'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}
