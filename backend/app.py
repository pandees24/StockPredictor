from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from models import db, User, Stock, StockData, Prediction, Watchlist, Alert
from config import config
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import bcrypt
import jwt
import os

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])

db.init_app(app)
jwt_manager = JWTManager(app)
CORS(app, origins=app.config['CORS_ORIGINS'])

# Authentication routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already taken'}), 400
    
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password.decode('utf-8')
    )
    
    db.session.add(user)
    db.session.commit()
    
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'message': 'User registered successfully',
        'token': token,
        'user': {'id': user.id, 'username': user.username, 'email': user.email}
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {'id': user.id, 'username': user.username, 'email': user.email}
    })

# Stock data routes
@app.route('/api/stocks/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    try:
        # Check if we have recent data in database
        stock = Stock.query.filter_by(symbol=symbol.upper()).first()
        if stock:
            cutoff_date = datetime.now() - timedelta(days=1)
            recent_data = StockData.query.filter(
                StockData.stock_id == stock.id,
                StockData.date >= cutoff_date.date()
            ).order_by(StockData.date).all()
            
            if recent_data:
                return jsonify([{
                    'date': data.date.isoformat(),
                    'open': data.open_price,
                    'high': data.high_price,
                    'low': data.low_price,
                    'close': data.close_price,
                    'volume': data.volume
                } for data in recent_data])
        
        # Fetch from yfinance if no recent data
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1y")
        
        if hist.empty:
            return jsonify({'message': 'Stock symbol not found'}), 404
        
        # Save to database
        if not stock:
            stock = Stock(symbol=symbol.upper(), name=ticker.info.get('longName', symbol))
            db.session.add(stock)
            db.session.commit()
        
        data_list = []
        for date, row in hist.iterrows():
            stock_data = StockData(
                stock_id=stock.id,
                date=date.date(),
                open_price=float(row['Open']),
                high_price=float(row['High']),
                low_price=float(row['Low']),
                close_price=float(row['Close']),
                volume=int(row['Volume'])
            )
            db.session.add(stock_data)
            data_list.append({
                'date': date.date().isoformat(),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            })
        
        db.session.commit()
        return jsonify(data_list)
    
    except Exception as e:
        return jsonify({'message': 'Error fetching stock data', 'error': str(e)}), 500

# Prediction routes
@app.route('/api/predictions/<symbol>', methods=['GET'])
@jwt_required()
def get_predictions(symbol):
    # This would integrate with the ML model
    # For now, return mock predictions
    return jsonify([
        round(150 + i * 0.5 + (i % 3) * 2, 2) for i in range(30)
    ])

# Watchlist routes
@app.route('/api/watchlist', methods=['GET'])
@jwt_required()
def get_watchlist():
    user_id = get_jwt_identity()['user_id']
    watchlist_items = Watchlist.query.filter_by(user_id=user_id).all()
    
    result = []
    for item in watchlist_items:
        stock = Stock.query.get(item.stock_id)
        result.append({
            'id': item.id,
            'symbol': stock.symbol,
            'name': stock.name,
            'added_at': item.added_at.isoformat()
        })
    
    return jsonify(result)

@app.route('/api/watchlist', methods=['POST'])
@jwt_required()
def add_to_watchlist():
    user_id = get_jwt_identity()['user_id']
    data = request.get_json()
    
    stock = Stock.query.filter_by(symbol=data['symbol'].upper()).first()
    if not stock:
        return jsonify({'message': 'Stock not found'}), 404
    
    if Watchlist.query.filter_by(user_id=user_id, stock_id=stock.id).first():
        return jsonify({'message': 'Stock already in watchlist'}), 400
    
    watchlist_item = Watchlist(user_id=user_id, stock_id=stock.id)
    db.session.add(watchlist_item)
    db.session.commit()
    
    return jsonify({'message': 'Added to watchlist'}), 201

@app.route('/api/watchlist/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_watchlist(item_id):
    user_id = get_jwt_identity()['user_id']
    item = Watchlist.query.filter_by(id=item_id, user_id=user_id).first()
    
    if not item:
        return jsonify({'message': 'Watchlist item not found'}), 404
    
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({'message': 'Removed from watchlist'})

# Alert routes
@app.route('/api/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    user_id = get_jwt_identity()['user_id']
    alerts = Alert.query.filter_by(user_id=user_id).all()
    
    result = []
    for alert in alerts:
        stock = Stock.query.get(alert.stock_id)
        result.append({
            'id': alert.id,
            'symbol': stock.symbol,
            'type': alert.alert_type,
            'price': alert.target_price,
            'triggered': alert.triggered,
            'triggeredAt': alert.triggered_at.isoformat() if alert.triggered_at else None
        })
    
    return jsonify(result)

@app.route('/api/alerts', methods=['POST'])
@jwt_required()
def create_alert():
    user_id = get_jwt_identity()['user_id']
    data = request.get_json()
    
    stock = Stock.query.filter_by(symbol=data['symbol'].upper()).first()
    if not stock:
        return jsonify({'message': 'Stock not found'}), 404
    
    alert = Alert(
        user_id=user_id,
        stock_id=stock.id,
        alert_type=data['type'],
        target_price=data['price']
    )
    
    db.session.add(alert)
    db.session.commit()
    
    return jsonify({'message': 'Alert created'}), 201

@app.route('/api/alerts/<int:alert_id>', methods=['DELETE'])
@jwt_required()
def delete_alert(alert_id):
    user_id = get_jwt_identity()['user_id']
    alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()
    
    if not alert:
        return jsonify({'message': 'Alert not found'}), 404
    
    db.session.delete(alert)
    db.session.commit()
    
    return jsonify({'message': 'Alert deleted'})

# Report routes
@app.route('/api/reports/<report_type>', methods=['GET'])
@jwt_required()
def generate_report(report_type):
    # This would generate actual reports
    # For now, return a placeholder
    return jsonify({'message': f'{report_type} report generated'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
