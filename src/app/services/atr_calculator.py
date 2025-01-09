import pandas as pd
import numpy as np
from typing import List, Dict
from binance.um_futures import UMFutures
import os
from dotenv import load_dotenv

load_dotenv()

def calculate_atr(klines: List[List], period: int = 14) -> float:
    """ATR değerini hesaplar"""
    # Klines verisini DataFrame'e çevir
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignored'])
    
    # String değerleri float'a çevir
    df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
    
    # True Range hesaplama
    df['tr1'] = df['high'] - df['low']
    df['tr2'] = abs(df['high'] - df['close'].shift())
    df['tr3'] = abs(df['low'] - df['close'].shift())
    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    
    # ATR hesaplama
    df['atr'] = df['tr'].rolling(window=period).mean()
    
    return {
        "atr": df['atr'].iloc[-1],
        "tr_values": df['tr'].tolist(),
        "atr_values": df['atr'].tolist()
    }

def get_atr_signals(symbol: str = "BTCUSDT", interval: str = "1h", period: int = 14, limit: int = 100):
    """ATR sinyalleri hesaplar"""
    try:
        client = UMFutures(
            key=os.getenv("BINANCE_TEST_API_KEY"),
            secret=os.getenv("BINANCE_TEST_API_SECRET"),
            base_url="https://testnet.binancefuture.com"
        )
        
        # Mum verilerini al
        klines = client.klines(symbol, interval, limit=limit)
        
        # ATR hesapla
        atr_data = calculate_atr(klines, period)
        
        # Mevcut fiyat
        current_price = float(client.mark_price(symbol)['markPrice'])
        
        # Sinyal seviyeleri
        take_profit = current_price + (atr_data['atr'] * 2.5)  # 2.5 ATR üstü
        stop_loss = current_price - atr_data['atr']  # 1 ATR altı
        
        return {
            "status": "success",
            "symbol": symbol,
            "current_price": current_price,
            "atr": atr_data['atr'],
            "signals": {
                "take_profit": take_profit,
                "stop_loss": stop_loss,
                "risk_reward_ratio": 2.5  # (TP - Entry) / (Entry - SL)
            },
            "analysis": {
                "tr_values": atr_data['tr_values'][-5:],  # Son 5 TR değeri
                "atr_values": atr_data['atr_values'][-5:],  # Son 5 ATR değeri
                "volatility_status": "HIGH" if atr_data['atr'] > np.mean(atr_data['atr_values']) else "LOW"
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        } 