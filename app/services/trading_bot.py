from binance.client import Client
from binance.um_futures import UMFutures
from typing import Dict, Optional
import logging
import os
from dotenv import load_dotenv
from ..utils.logger import logger

load_dotenv()

class TradingBot:
    def __init__(self, symbol: str, atr_multiplier: float = 2.5):
        self.client = UMFutures(
            key=os.getenv("BINANCE_TEST_API_KEY"),
            secret=os.getenv("BINANCE_TEST_API_SECRET"),
            base_url="https://testnet.binancefuture.com"
        )
        logger.info(f"TradingBot initialized for {symbol} with ATR multiplier {atr_multiplier}")
        self.symbol = symbol
        self.atr_multiplier = atr_multiplier
        self.position = None
        self.entry_price = None
        self.position_size = None
        
    async def check_and_enter_position(self, current_price: float, atr: float):
        """ATR'ye göre yeni pozisyon açma kontrolü"""
        try:
            logger.info(f"Checking position entry conditions. Current price: {current_price}, ATR: {atr}")
            # Pozisyon yoksa ve giriş koşulları uygunsa
            if not self.position:
                # Market emri ile long pozisyon aç
                order = await self.place_order("BUY", self.calculate_position_size())
                self.position = "LONG"
                self.entry_price = float(order['avgPrice'])
                self.position_size = float(order['executedQty'])
                
                # TP ve SL emirlerini yerleştir
                take_profit = self.entry_price + (atr * self.atr_multiplier)
                stop_loss = self.entry_price - atr
                
                logger.info(f"Position opened - Entry: {self.entry_price}, TP: {take_profit}, SL: {stop_loss}")
                
                # TP emri
                await self.place_order(
                    side="SELL",
                    quantity=self.position_size,
                    price=take_profit,
                    order_type="TAKE_PROFIT_MARKET",
                    stop_price=take_profit
                )
                
                # SL emri
                await self.place_order(
                    side="SELL",
                    quantity=self.position_size,
                    price=stop_loss,
                    order_type="STOP_MARKET",
                    stop_price=stop_loss
                )
                
                return {
                    "action": "OPENED_LONG",
                    "entry_price": self.entry_price,
                    "position_size": self.position_size,
                    "take_profit": take_profit,
                    "stop_loss": stop_loss
                }
                
        except Exception as e:
            logger.error(f"Position entry error: {str(e)}")
            raise
            
    async def place_order(self, side: str, quantity: float, price: Optional[float] = None, 
                         order_type: str = "MARKET", stop_price: Optional[float] = None) -> Dict:
        """Emir yerleştirme"""
        try:
            logger.info(f"Placing order - Side: {side}, Type: {order_type}, Quantity: {quantity}, Price: {price}, Stop: {stop_price}")
            params = {
                "symbol": self.symbol,
                "side": side,
                "type": order_type,
                "quantity": quantity
            }
            
            if price:
                params["price"] = price
            if stop_price:
                params["stopPrice"] = stop_price
            if order_type in ["LIMIT", "TAKE_PROFIT_LIMIT", "STOP_LIMIT"]:
                params["timeInForce"] = "GTC"
                
            order = self.client.new_order(**params)
            logger.info(f"Order placed successfully: {order}")
            return order
            
        except Exception as e:
            logger.error(f"Order placement error: {str(e)}")
            raise
            
    def calculate_position_size(self) -> float:
        """Pozisyon büyüklüğünü hesapla"""
        try:
            balance = float(self.client.balance()['totalWalletBalance'])
            current_price = float(self.client.mark_price(self.symbol)['markPrice'])
            
            # Bakiyenin %1'i ile işlem yap
            quantity = (balance * 0.01) / current_price
            
            # Lot büyüklüğüne göre yuvarla
            info = self.client.exchange_info()
            symbol_info = next(item for item in info['symbols'] if item['symbol'] == self.symbol)
            lot_size_filter = next(item for item in symbol_info['filters'] if item['filterType'] == 'LOT_SIZE')
            step_size = float(lot_size_filter['stepSize'])
            
            quantity = round(quantity - (quantity % step_size), 8)
            logger.info(f"Calculated position size: {quantity}")
            return quantity
            
        except Exception as e:
            logger.error(f"Position size calculation error: {str(e)}")
            raise 