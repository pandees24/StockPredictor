import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './Dashboard.css';

const Dashboard = () => {
  const [stockData, setStockData] = useState([]);
  const [selectedStock, setSelectedStock] = useState('AAPL');
  const [searchTerm, setSearchTerm] = useState('');
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStockData();
    fetchPredictions();
  }, [selectedStock]);

  const fetchStockData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:5000/api/stocks/${selectedStock}`);
      setStockData(response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch stock data');
    } finally {
      setLoading(false);
    }
  };

  const fetchPredictions = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/predictions/${selectedStock}`);
      setPredictions(response.data);
    } catch (err) {
      console.error('Failed to fetch predictions');
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      setSelectedStock(searchTerm.toUpperCase());
      setSearchTerm('');
    }
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>StockPredictor Dashboard</h1>
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Enter stock symbol (e.g., AAPL)"
            className="search-input"
          />
          <button type="submit" className="search-button">Search</button>
        </form>
      </header>

      <div className="dashboard-content">
        {loading && <div className="loading">Loading...</div>}
        {error && <div className="error">{error}</div>}

        <div className="chart-container">
          <h2>{selectedStock} Stock Price Chart</h2>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={stockData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="close" stroke="#8884d8" name="Close Price" />
              {predictions.length > 0 && (
                <Line type="monotone" dataKey="predicted" stroke="#82ca9d" name="Predicted" strokeDasharray="5 5" />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="predictions-container">
          <h2>30-Day Predictions</h2>
          {predictions.length > 0 ? (
            <ul className="predictions-list">
              {predictions.slice(0, 30).map((pred, index) => (
                <li key={index} className="prediction-item">
                  Day {index + 1}: ${pred.toFixed(2)}
                </li>
              ))}
            </ul>
          ) : (
            <p>No predictions available</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
