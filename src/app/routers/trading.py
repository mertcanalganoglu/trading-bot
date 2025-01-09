from fastapi import APIRouter, HTTPException
from typing import Dict
from ..services.atr_calculator import calculate_atr, get_atr_signals
from ..services.trading_bot import TradingBot
from binance.um_futures import UMFutures
import os
from dotenv import load_dotenv
from ..utils.logger import logger  # Logger'ı import et
from datetime import datetime

load_dotenv()

router = APIRouter()

@router.post("/start-trading")
async def start_trading(symbol: str, atr_multiplier: float = 2.5) -> Dict:
    try:
        client = UMFutures(
            key=os.getenv("BINANCE_TEST_API_KEY"),
            secret=os.getenv("BINANCE_TEST_API_SECRET"),
            base_url="https://testnet.binancefuture.com"
        )
        
        # Son fiyat verilerini al
        klines = client.get_klines(
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_1HOUR,
            limit=100
        )
        
        # ATR hesapla
        atr = calculate_atr(klines)
        
        # Trading bot başlat
        bot = TradingBot(symbol, atr_multiplier)
        current_price = float(client.get_symbol_ticker(symbol=symbol)['price'])
        
        result = await bot.execute_strategy(current_price, atr)
        
        return {
            "status": "success",
            "message": "Trading started",
            "atr": atr,
            "current_price": current_price,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-balance")
async def test_balance():
    try:
        client = UMFutures(
            key=os.getenv("BINANCE_TEST_API_KEY"),
            secret=os.getenv("BINANCE_TEST_API_SECRET"),
            base_url="https://testnet.binancefuture.com"
        )
        
        # Futures hesap bilgilerini al
        account = client.account()
        
        return {
            "status": "success",
            "message": "Test balance retrieved",
            "account": account
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-market-data")
async def test_market_data(symbol: str = "BTCUSDT"):
    try:
        client = UMFutures(
            key=os.getenv("BINANCE_TEST_API_KEY"),
            secret=os.getenv("BINANCE_TEST_API_SECRET"),
            base_url="https://testnet.binancefuture.com"
        )
        
        # Futures fiyat bilgisini al
        ticker = client.mark_price(symbol)
        
        return {
            "status": "success",
            "message": "Test market data retrieved",
            "price": ticker['markPrice']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mevcut pozisyonları kontrol et
@router.get("/positions")
async def get_positions(symbol: str = "BTCUSDT"):
    try:
        logger.info(f"Getting positions for {symbol}")
        client = UMFutures(
            key=os.getenv("BINANCE_TEST_API_KEY"),
            secret=os.getenv("BINANCE_TEST_API_SECRET"),
            base_url="https://testnet.binancefuture.com"
        )
        
        positions = client.get_position_risk(symbol=symbol)
        logger.info(f"Positions retrieved: {positions}")
        
        return {
            "status": "success",
            "message": "Positions retrieved",
            "positions": positions
        }
    except Exception as e:
        logger.error(f"Error getting positions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Kaldıraç ayarla
@router.post("/set-leverage")
async def set_leverage(symbol: str = "BTCUSDT", leverage: int = 5):
    try:
        client = UMFutures(
            key=os.getenv("BINANCE_TEST_API_KEY"),
            secret=os.getenv("BINANCE_TEST_API_SECRET"),
            base_url="https://testnet.binancefuture.com"
        )
        
        response = client.change_leverage(
            symbol=symbol,
            leverage=leverage
        )
        
        return {
            "status": "success",
            "message": f"Leverage set to {leverage}x",
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Marjin tipi değiştir (ISOLATED veya CROSSED)
@router.post("/change-margin-type")
async def change_margin_type(symbol: str = "BTCUSDT", margin_type: str = "ISOLATED"):
    try:
        client = UMFutures(
            key=os.getenv("BINANCE_TEST_API_KEY"),
            secret=os.getenv("BINANCE_TEST_API_SECRET"),
            base_url="https://testnet.binancefuture.com"
        )
        
        response = client.change_margin_type(
            symbol=symbol,
            marginType=margin_type
        )
        
        return {
            "status": "success",
            "message": f"Margin type changed to {margin_type}",
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Tüm açık emirleri iptal et
@router.delete("/cancel-orders")
async def cancel_all_orders(symbol: str = "BTCUSDT"):
    try:
        client = UMFutures(
            key=os.getenv("BINANCE_TEST_API_KEY"),
            secret=os.getenv("BINANCE_TEST_API_SECRET"),
            base_url="https://testnet.binancefuture.com"
        )
        
        response = client.cancel_open_orders(symbol=symbol)
        
        return {
            "status": "success",
            "message": "All open orders cancelled",
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Piyasa fiyatından pozisyon aç
@router.post("/market-order")
async def place_market_order(
    symbol: str = "BTCUSDT",
    side: str = "BUY",
    quantity: float = 0.001
):
    try:
        logger.info(f"Placing market order: {side} {quantity} {symbol}")
        client = UMFutures(
            key=os.getenv("BINANCE_TEST_API_KEY"),
            secret=os.getenv("BINANCE_TEST_API_SECRET"),
            base_url="https://testnet.binancefuture.com"
        )
        
        order = client.new_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity
        )
        logger.info(f"Order placed successfully: {order}")
        
        return {
            "status": "success",
            "message": f"Market order placed: {side} {quantity} {symbol}",
            "order": order
        }
    except Exception as e:
        logger.error(f"Error placing market order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Stop-limit emri ver
@router.post("/stop-limit-order")
async def place_stop_limit_order(
    symbol: str = "BTCUSDT",
    side: str = "SELL",
    quantity: float = 0.001,
    stop_price: float = None,
    limit_price: float = None
):
    try:
        client = UMFutures(
            key=os.getenv("BINANCE_TEST_API_KEY"),
            secret=os.getenv("BINANCE_TEST_API_SECRET"),
            base_url="https://testnet.binancefuture.com"
        )
        
        # Eğer fiyatlar belirtilmemişse mevcut fiyattan hesapla
        if not stop_price or not limit_price:
            current_price = float(client.mark_price(symbol)['markPrice'])
            if side == "SELL":
                stop_price = current_price * 0.99  # %1 altında
                limit_price = stop_price * 0.99
            else:
                stop_price = current_price * 1.01  # %1 üstünde
                limit_price = stop_price * 1.01
        
        order = client.new_order(
            symbol=symbol,
            side=side,
            type="STOP",
            quantity=quantity,
            stopPrice=stop_price,
            price=limit_price,
            timeInForce="GTC"
        )
        
        return {
            "status": "success",
            "message": f"Stop-limit order placed",
            "order": order
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_logs(lines: int = 100):
    try:
        log_directory = "logs"
        today = datetime.now().strftime('%Y%m%d')
        log_file = f"{log_directory}/trading_{today}.log"
        
        if not os.path.exists(log_file):
            return {
                "status": "error",
                "message": "No logs found for today"
            }
            
        # Son n satır logu oku
        with open(log_file, 'r') as f:
            logs = f.readlines()[-lines:]
            
        return {
            "status": "success",
            "logs": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/error-logs")
async def get_error_logs(lines: int = 100):
    try:
        log_directory = "logs"
        today = datetime.now().strftime('%Y%m%d')
        log_file = f"{log_directory}/trading_{today}.log"
        
        if not os.path.exists(log_file):
            return {
                "status": "error",
                "message": "No logs found for today"
            }
            
        # Hata loglarını filtrele
        with open(log_file, 'r') as f:
            all_logs = f.readlines()
            error_logs = [log for log in all_logs if "ERROR" in log][-lines:]
            
        return {
            "status": "success",
            "error_logs": error_logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/atr-analysis")
async def get_atr_analysis(
    symbol: str = "BTCUSDT",
    interval: str = "1h",
    period: int = 14
):
    try:
        logger.info(f"Getting ATR analysis for {symbol}")
        
        result = get_atr_signals(symbol, interval, period)
        
        if result["status"] == "error":
            logger.error(f"Error in ATR analysis: {result['message']}")
            raise HTTPException(status_code=500, detail=result['message'])
            
        logger.info(f"ATR analysis completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in ATR analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auto-trade")
async def start_auto_trading(
    symbol: str = "BTCUSDT",
    atr_multiplier: float = 2.5,
    interval: str = "1h"
):
    try:
        logger.info(f"Starting auto trading for {symbol}")
        
        # ATR hesapla
        atr_data = get_atr_signals(symbol, interval)
        
        if atr_data["status"] == "error":
            raise HTTPException(status_code=500, detail=atr_data["message"])
            
        # Trading bot başlat
        bot = TradingBot(symbol, atr_multiplier)
        
        # Pozisyon kontrolü ve açma
        result = await bot.check_and_enter_position(
            current_price=atr_data["current_price"],
            atr=atr_data["atr"]
        )
        
        return {
            "status": "success",
            "message": "Auto trading started",
            "symbol": symbol,
            "atr": atr_data["atr"],
            "current_price": atr_data["current_price"],
            "trading_result": result
        }
        
    except Exception as e:
        logger.error(f"Auto trading error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-connection")
async def test_connection():
    try:
        client = UMFutures(
            key=os.getenv("BINANCE_TEST_API_KEY"),
            secret=os.getenv("BINANCE_TEST_API_SECRET"),
            base_url="https://testnet.binancefuture.com"
        )
        
        # Test bağlantısı
        time = client.time()
        
        return {
            "status": "success",
            "message": "Connection successful",
            "server_time": time
        }
    except Exception as e:
        logger.error(f"Connection test error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 