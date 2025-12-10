import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Alerts.css';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [newAlert, setNewAlert] = useState({ symbol: '', price: '', type: 'above' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:5000/api/alerts', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setAlerts(response.data);
    } catch (err) {
      setError('Failed to fetch alerts');
    } finally {
      setLoading(false);
    }
  };

  const addAlert = async (e) => {
    e.preventDefault();
    if (!newAlert.symbol || !newAlert.price) return;
    
    try {
      await axios.post('http://localhost:5000/api/alerts', newAlert, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setNewAlert({ symbol: '', price: '', type: 'above' });
      fetchAlerts();
    } catch (err) {
      setError('Failed to add alert');
    }
  };

  const removeAlert = async (id) => {
    try {
      await axios.delete(`http://localhost:5000/api/alerts/${id}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      fetchAlerts();
    } catch (err) {
      setError('Failed to remove alert');
    }
  };

  return (
    <div className="alerts">
      <h1>Price Alerts</h1>
      
      {error && <div className="error">{error}</div>}
      
      <div className="alerts-content">
        <div className="add-alert-section">
          <h2>Add New Alert</h2>
          <form onSubmit={addAlert} className="add-alert-form">
            <div className="form-group">
              <label htmlFor="symbol">Stock Symbol</label>
              <input
                type="text"
                id="symbol"
                value={newAlert.symbol}
                onChange={(e) => setNewAlert({...newAlert, symbol: e.target.value.toUpperCase()})}
                placeholder="e.g., AAPL"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="type">Alert Type</label>
              <select
                id="type"
                value={newAlert.type}
                onChange={(e) => setNewAlert({...newAlert, type: e.target.value})}
              >
                <option value="above">Price goes above</option>
                <option value="below">Price goes below</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="price">Target Price</label>
              <input
                type="number"
                id="price"
                value={newAlert.price}
                onChange={(e) => setNewAlert({...newAlert, price: parseFloat(e.target.value) || ''})}
                placeholder="0.00"
                step="0.01"
                min="0"
                required
              />
            </div>
            <button type="submit" className="add-alert-button">Add Alert</button>
          </form>
        </div>

        <div className="alerts-list-section">
          <h2>Active Alerts</h2>
          {loading ? (
            <div className="loading">Loading alerts...</div>
          ) : alerts.length === 0 ? (
            <p className="no-alerts">No active alerts. Add one above to get started!</p>
          ) : (
            <div className="alerts-list">
              {alerts.map((alert) => (
                <div key={alert.id} className={`alert-item ${alert.triggered ? 'triggered' : ''}`}>
                  <div className="alert-info">
                    <h3>{alert.symbol}</h3>
                    <p>Alert when price goes {alert.type} ${alert.price.toFixed(2)}</p>
                    <p className="alert-status">
                      Status: <span className={alert.triggered ? 'triggered-text' : 'active-text'}>
                        {alert.triggered ? 'Triggered' : 'Active'}
                      </span>
                    </p>
                    {alert.triggered && (
                      <p className="trigger-time">Triggered at: {new Date(alert.triggeredAt).toLocaleString()}</p>
                    )}
                  </div>
                  <button 
                    onClick={() => removeAlert(alert.id)}
                    className="remove-alert-button"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Alerts;
