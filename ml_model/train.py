import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import yfinance as yf
import pickle
import os

def fetch_stock_data(symbol, period="5y"):
    """Fetch historical stock data from Yahoo Finance"""
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    return df[['Close']].dropna()

def prepare_data(data, lookback=60):
    """Prepare data for LSTM training"""
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    
    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i-lookback:i, 0])
        y.append(scaled_data[i, 0])
    
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    
    return X, y, scaler

def build_model(input_shape):
    """Build LSTM model"""
    model = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(units=50, return_sequences=True),
        Dropout(0.2),
        LSTM(units=50),
        Dropout(0.2),
        Dense(units=1)
    ])
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def train_model(symbol, epochs=100, batch_size=32):
    """Train LSTM model for stock prediction"""
    print(f"Fetching data for {symbol}...")
    data = fetch_stock_data(symbol)
    
    if len(data) < 100:
        raise ValueError("Not enough data for training")
    
    print("Preparing data...")
    X, y, scaler = prepare_data(data.values)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Building model...")
    model = build_model((X.shape[1], 1))
    
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    
    print("Training model...")
    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_test, y_test),
        callbacks=[early_stopping],
        verbose=1
    )
    
    # Evaluate model
    loss = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Loss: {loss}")
    
    # Save model and scaler
    os.makedirs('models', exist_ok=True)
    model.save(f'models/{symbol}_model.h5')
    
    with open(f'models/{symbol}_scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    print(f"Model saved for {symbol}")
    return model, scaler, history

def predict_future(model, scaler, last_data, days=30):
    """Predict future stock prices"""
    predictions = []
    current_input = last_data[-60:].reshape(1, 60, 1)
    
    for _ in range(days):
        pred = model.predict(current_input, verbose=0)
        predictions.append(pred[0][0])
        
        # Update input for next prediction
        current_input = np.roll(current_input, -1)
        current_input[0, -1, 0] = pred[0][0]
    
    # Inverse transform predictions
    predictions = np.array(predictions).reshape(-1, 1)
    predictions = scaler.inverse_transform(predictions)
    
    return predictions.flatten()

if __name__ == "__main__":
    # Train models for popular stocks
    stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    
    for stock in stocks:
        try:
            print(f"\nTraining model for {stock}...")
            model, scaler, history = train_model(stock)
            print(f"Successfully trained model for {stock}")
        except Exception as e:
            print(f"Failed to train model for {stock}: {e}")
    
    print("\nTraining completed!")
