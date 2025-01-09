from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from binance.client import Client
import pandas as pd
import numpy as np
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Binance client
api_key = os.getenv('BINANCE_TEST_API_KEY')
api_secret = os.getenv('BINANCE_TEST_API_SECRET')
client = Client(api_key, api_secret, testnet=True)

def calculate_atr(high, low, close, period=14):
    tr1 = pd.DataFrame(high - low)
    tr2 = pd.DataFrame(abs(high - close.shift()))
    tr3 = pd.DataFrame(abs(low - close.shift()))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

@app.get("/api/v1/atr-analysis")
async def get_atr_analysis(symbol: str, interval: str = "1h"):
    try:
        # Get klines data from Binance
        klines = client.get_klines(symbol=symbol, interval=interval, limit=100)
        
        # Convert to DataFrame
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                         'close_time', 'quote_asset_volume', 'number_of_trades',
                                         'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        
        # Convert price columns to float
        for col in ['open', 'high', 'low', 'close']:
            df[col] = df[col].astype(float)
        
        # Calculate ATR
        atr = calculate_atr(df['high'], df['low'], df['close'])
        current_atr = atr.iloc[-1]
        
        # Generate signals based on ATR
        signals = []
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1] + current_atr:
                signals.append({
                    'time': df['timestamp'].iloc[i],
                    'type': 'buy',
                    'price': df['close'].iloc[i]
                })
            elif df['close'].iloc[i] < df['close'].iloc[i-1] - current_atr:
                signals.append({
                    'time': df['timestamp'].iloc[i],
                    'type': 'sell',
                    'price': df['close'].iloc[i]
                })
        
        return {
            "klines": klines,
            "atr": current_atr,
            "signals": signals
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 