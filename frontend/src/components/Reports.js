import React, { useState } from 'react';
import axios from 'axios';
import './Reports.css';

const Reports = () => {
  const [reportType, setReportType] = useState('portfolio');
  const [dateRange, setDateRange] = useState('30d');
  const [generating, setGenerating] = useState(false);

  const generateReport = async () => {
    setGenerating(true);
    try {
      const response = await axios.get(`http://localhost:5000/api/reports/${reportType}?range=${dateRange}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${reportType}_report_${dateRange}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Failed to generate report');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="reports">
      <h1>Reports</h1>
      <div className="report-controls">
        <div className="control-group">
          <label>Report Type:</label>
          <select value={reportType} onChange={(e) => setReportType(e.target.value)}>
            <option value="portfolio">Portfolio Performance</option>
            <option value="predictions">Prediction Accuracy</option>
            <option value="transactions">Transaction History</option>
          </select>
        </div>
        <div className="control-group">
          <label>Date Range:</label>
          <select value={dateRange} onChange={(e) => setDateRange(e.target.value)}>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
        </div>
        <button 
          onClick={generateReport} 
          disabled={generating}
          className="generate-button"
        >
          {generating ? 'Generating...' : 'Generate PDF Report'}
        </button>
      </div>
      <div className="report-info">
        <h2>Report Types</h2>
        <div className="report-types">
          <div className="report-type">
            <h3>Portfolio Performance</h3>
            <p>Comprehensive overview of your portfolio's performance, including gains/losses, asset allocation, and historical trends.</p>
          </div>
          <div className="report-type">
            <h3>Prediction Accuracy</h3>
            <p>Analysis of the accuracy of stock price predictions made by the system, including success rates and error margins.</p>
          </div>
          <div className="report-type">
            <h3>Transaction History</h3>
            <p>Detailed log of all your trading activities, including buy/sell orders, dates, prices, and transaction fees.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reports;
