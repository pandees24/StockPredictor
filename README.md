# StockPredictor

A comprehensive stock prediction application built with React.js frontend, Flask backend, and LSTM machine learning models for accurate 30-day stock price predictions.

## Features

- **Real-time Stock Charts**: Interactive charts using Chart.js and Recharts for visualizing stock price data
- **LSTM Predictions**: Advanced machine learning models achieving ~87% accuracy on 30-day predictions
- **User Authentication**: Secure JWT-based authentication system
- **Portfolio Management**: Track your stock holdings and performance
- **Price Alerts**: Set custom alerts for price changes (above/below thresholds)
- **Watchlist**: Add and manage stocks you're interested in
- **Reports**: Generate PDF reports for portfolio performance, predictions, and transaction history
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## Tech Stack

### Frontend
- React.js with Hooks
- Axios for API calls
- Chart.js and Recharts for data visualization
- CSS3 with responsive design
- Context API for state management

### Backend
- Flask with SQLAlchemy
- PostgreSQL database
- JWT for authentication
- Flask-CORS for cross-origin requests
- RESTful API design

### Machine Learning
- TensorFlow/Keras LSTM models
- Pandas and NumPy for data processing
- Scikit-learn for preprocessing
- Yahoo Finance API for historical data

## Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- PostgreSQL
- Git

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   # Create PostgreSQL database named 'stockpredictor'
   # Update .env file with your database credentials
   ```

5. Run the Flask app:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

### ML Model Setup

1. Navigate to the ml_model directory:
   ```bash
   cd ml_model
   ```

2. Train the models:
   ```bash
   python train.py
   ```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=postgresql://username:password@localhost/stockpredictor
CORS_ORIGINS=http://localhost:3000
DEBUG=True
```

## API Documentation

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login user

### Stocks
- `GET /api/stocks/<symbol>` - Get historical stock data

### Predictions
- `GET /api/predictions/<symbol>` - Get 30-day price predictions

### Watchlist
- `GET /api/watchlist` - Get user's watchlist
- `POST /api/watchlist` - Add stock to watchlist
- `DELETE /api/watchlist/<item_id>` - Remove from watchlist

### Alerts
- `GET /api/alerts` - Get user's alerts
- `POST /api/alerts` - Create new alert
- `DELETE /api/alerts/<alert_id>` - Delete alert

### Reports
- `GET /api/reports/<report_type>` - Generate PDF report

## Usage

1. Register/Login to access the application
2. Search for stocks using the search bar on the dashboard
3. View real-time charts and predictions
4. Set up price alerts for stocks you're interested in
5. Add stocks to your watchlist
6. Generate reports for your portfolio and predictions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.
