"""
Bybit WebSocket Manager for Nuclear Swarm
Real-time market data for high-frequency trading
"""

import asyncio
import json
import websockets
import time
from typing import Dict, List, Callable, Optional
from datetime import datetime
from collections import defaultdict


class BybitWebSocket:
    """Bybit WebSocket for real-time market data"""

    def __init__(self, testnet: bool = True):
        """
        Initialize Bybit WebSocket

        Args:
            testnet: Use testnet (True) or live (False)
        """
        self.testnet = testnet

        # WebSocket URLs
        if testnet:
            self.ws_url = "wss://stream-testnet.bybit.com/realtime"
        else:
            self.ws_url = "wss://stream.bybit.com/realtime"

        # Connection
        self.ws = None
        self.is_connected = False
        self.reconnect_delay = 5

        # Subscriptions
        self.subscribed_symbols = set()
        self.subscribed_channels = set()

        # Data storage
        self.tickers = {}
        self.orderbooks = defaultdict(lambda: {'bids': {}, 'asks': {}})
        self.trades = defaultdict(list)
        self.klines = defaultdict(lambda: defaultdict(list))

        # Callbacks
        self.ticker_callbacks = []
        self.orderbook_callbacks = []
        self.trade_callbacks = []
        self.kline_callbacks = []

        # Stats
        self.messages_received = 0
        self.last_message_time = None
        self.latency_ms = 0

        print(f"✅ Bybit WebSocket initialized ({'TESTNET' if testnet else 'LIVE'})")

    async def connect(self):
        """Establish WebSocket connection"""
        try:
            self.ws = await websockets.connect(self.ws_url, ping_interval=20)
            self.is_connected = True
            print(f"✅ Connected to Bybit WebSocket")

            # Start message handler
            asyncio.create_task(self._handle_messages())

            return True

        except Exception as e:
            print(f"❌ WebSocket connection failed: {str(e)}")
            self.is_connected = False
            return False

    async def disconnect(self):
        """Close WebSocket connection"""
        if self.ws:
            await self.ws.close()
            self.is_connected = False
            print("🔌 WebSocket disconnected")

    async def subscribe_ticker(self, symbols: List[str]):
        """
        Subscribe to ticker updates

        Args:
            symbols: List of symbols (e.g., ['BTCUSDT', 'ETHUSDT'])
        """
        for symbol in symbols:
            topic = f"instrument_info.100ms.{symbol}"
            await self._subscribe(topic)
            self.subscribed_symbols.add(symbol)
            print(f"📊 Subscribed to ticker: {symbol}")

    async def subscribe_orderbook(self, symbols: List[str], depth: int = 25):
        """
        Subscribe to orderbook updates

        Args:
            symbols: List of symbols
            depth: Orderbook depth (25, 50, 100, 200)
        """
        for symbol in symbols:
            topic = f"orderBook_200.100ms.{symbol}"
            await self._subscribe(topic)
            self.subscribed_symbols.add(symbol)
            print(f"📖 Subscribed to orderbook: {symbol}")

    async def subscribe_trades(self, symbols: List[str]):
        """
        Subscribe to trade updates

        Args:
            symbols: List of symbols
        """
        for symbol in symbols:
            topic = f"trade.{symbol}"
            await self._subscribe(topic)
            self.subscribed_symbols.add(symbol)
            print(f"💱 Subscribed to trades: {symbol}")

    async def subscribe_klines(self, symbols: List[str], intervals: List[str] = ['1', '3', '5']):
        """
        Subscribe to kline (candlestick) updates

        Args:
            symbols: List of symbols
            intervals: Intervals in minutes (['1', '3', '5', '15', '30', '60'])
        """
        for symbol in symbols:
            for interval in intervals:
                topic = f"klineV2.{interval}.{symbol}"
                await self._subscribe(topic)
                self.subscribed_symbols.add(symbol)
                print(f"🕯️ Subscribed to {interval}m klines: {symbol}")

    async def _subscribe(self, topic: str):
        """Send subscription request"""
        if not self.is_connected:
            print("❌ Not connected to WebSocket")
            return

        subscribe_msg = {
            "op": "subscribe",
            "args": [topic]
        }

        try:
            await self.ws.send(json.dumps(subscribe_msg))
            self.subscribed_channels.add(topic)
        except Exception as e:
            print(f"❌ Subscription failed for {topic}: {str(e)}")

    async def _handle_messages(self):
        """Handle incoming WebSocket messages"""
        try:
            async for message in self.ws:
                receive_time = time.time()
                self.messages_received += 1
                self.last_message_time = receive_time

                try:
                    data = json.loads(message)

                    # Handle different message types
                    if 'topic' in data:
                        topic = data['topic']

                        # Ticker updates
                        if 'instrument_info' in topic:
                            await self._handle_ticker(data, receive_time)

                        # Orderbook updates
                        elif 'orderBook' in topic:
                            await self._handle_orderbook(data, receive_time)

                        # Trade updates
                        elif 'trade' in topic:
                            await self._handle_trade(data, receive_time)

                        # Kline updates
                        elif 'klineV2' in topic:
                            await self._handle_kline(data, receive_time)

                    # Subscription confirmations
                    elif data.get('success'):
                        pass  # Subscription confirmed

                    # Pong responses
                    elif 'pong' in data.get('ret_msg', ''):
                        pass  # Heartbeat response

                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON: {message}")
                except Exception as e:
                    print(f"❌ Message handling error: {str(e)}")

        except websockets.exceptions.ConnectionClosed:
            print("⚠️ WebSocket connection closed")
            self.is_connected = False
            await self._reconnect()
        except Exception as e:
            print(f"❌ WebSocket error: {str(e)}")
            self.is_connected = False

    async def _handle_ticker(self, data: Dict, receive_time: float):
        """Process ticker updates"""
        try:
            ticker_data = data['data']
            symbol = ticker_data['symbol']

            # Calculate latency
            update_time = ticker_data.get('update_time_e6', 0) / 1_000_000
            latency_ms = (receive_time - update_time) * 1000 if update_time > 0 else 0
            self.latency_ms = latency_ms

            # Store ticker
            self.tickers[symbol] = {
                'symbol': symbol,
                'last_price': float(ticker_data.get('last_price_e4', 0)) / 10000,
                'bid': float(ticker_data.get('bid1_price_e4', 0)) / 10000,
                'ask': float(ticker_data.get('ask1_price_e4', 0)) / 10000,
                'volume_24h': float(ticker_data.get('volume_24h_e8', 0)) / 100_000_000,
                'price_change_pct': float(ticker_data.get('price_24h_pcnt_e6', 0)) / 10000,
                'timestamp': receive_time,
                'latency_ms': latency_ms
            }

            # Call callbacks
            for callback in self.ticker_callbacks:
                callback(self.tickers[symbol])

        except Exception as e:
            print(f"❌ Ticker processing error: {str(e)}")

    async def _handle_orderbook(self, data: Dict, receive_time: float):
        """Process orderbook updates"""
        try:
            if 'data' not in data:
                return

            orderbook_data = data['data']
            symbol = data['topic'].split('.')[-1]

            # Update orderbook
            if 'delete' in orderbook_data:
                # Delete orders
                for delete_item in orderbook_data['delete']:
                    price = float(delete_item['price'])
                    side = delete_item['side']
                    if side == 'Buy':
                        self.orderbooks[symbol]['bids'].pop(price, None)
                    else:
                        self.orderbooks[symbol]['asks'].pop(price, None)

            if 'update' in orderbook_data:
                # Update orders
                for update_item in orderbook_data['update']:
                    price = float(update_item['price'])
                    size = float(update_item['size'])
                    side = update_item['side']
                    if side == 'Buy':
                        self.orderbooks[symbol]['bids'][price] = size
                    else:
                        self.orderbooks[symbol]['asks'][price] = size

            if 'insert' in orderbook_data:
                # Insert new orders
                for insert_item in orderbook_data['insert']:
                    price = float(insert_item['price'])
                    size = float(insert_item['size'])
                    side = insert_item['side']
                    if side == 'Buy':
                        self.orderbooks[symbol]['bids'][price] = size
                    else:
                        self.orderbooks[symbol]['asks'][price] = size

            # Sort and trim orderbook
            sorted_bids = sorted(self.orderbooks[symbol]['bids'].items(), reverse=True)[:25]
            sorted_asks = sorted(self.orderbooks[symbol]['asks'].items())[:25]

            orderbook = {
                'symbol': symbol,
                'bids': sorted_bids,
                'asks': sorted_asks,
                'timestamp': receive_time
            }

            # Call callbacks
            for callback in self.orderbook_callbacks:
                callback(orderbook)

        except Exception as e:
            print(f"❌ Orderbook processing error: {str(e)}")

    async def _handle_trade(self, data: Dict, receive_time: float):
        """Process trade updates"""
        try:
            if 'data' not in data:
                return

            symbol = data['topic'].split('.')[-1]

            for trade in data['data']:
                trade_data = {
                    'symbol': symbol,
                    'price': float(trade['price']),
                    'size': float(trade['size']),
                    'side': trade['side'],
                    'timestamp': receive_time,
                    'trade_time': trade.get('trade_time_ms', 0) / 1000
                }

                # Store recent trades (keep last 100)
                self.trades[symbol].append(trade_data)
                if len(self.trades[symbol]) > 100:
                    self.trades[symbol] = self.trades[symbol][-100:]

                # Call callbacks
                for callback in self.trade_callbacks:
                    callback(trade_data)

        except Exception as e:
            print(f"❌ Trade processing error: {str(e)}")

    async def _handle_kline(self, data: Dict, receive_time: float):
        """Process kline (candlestick) updates"""
        try:
            if 'data' not in data:
                return

            topic = data['topic']
            parts = topic.split('.')
            interval = parts[1]
            symbol = parts[2]

            for kline in data['data']:
                kline_data = {
                    'symbol': symbol,
                    'interval': interval,
                    'open': float(kline['open']),
                    'high': float(kline['high']),
                    'low': float(kline['low']),
                    'close': float(kline['close']),
                    'volume': float(kline['volume']),
                    'timestamp': kline['start'],
                    'confirmed': kline.get('confirm', False)
                }

                # Store kline
                self.klines[symbol][interval].append(kline_data)
                if len(self.klines[symbol][interval]) > 100:
                    self.klines[symbol][interval] = self.klines[symbol][interval][-100:]

                # Call callbacks
                for callback in self.kline_callbacks:
                    callback(kline_data)

        except Exception as e:
            print(f"❌ Kline processing error: {str(e)}")

    async def _reconnect(self):
        """Reconnect to WebSocket"""
        print(f"🔄 Reconnecting in {self.reconnect_delay} seconds...")
        await asyncio.sleep(self.reconnect_delay)

        if await self.connect():
            # Re-subscribe to all channels
            for channel in list(self.subscribed_channels):
                parts = channel.split('.')
                if 'instrument_info' in channel:
                    symbols = [parts[-1]]
                    await self.subscribe_ticker(symbols)
                elif 'orderBook' in channel:
                    symbols = [parts[-1]]
                    await self.subscribe_orderbook(symbols)
                elif 'trade' in channel:
                    symbols = [parts[-1]]
                    await self.subscribe_trades(symbols)
                elif 'klineV2' in channel:
                    symbols = [parts[-1]]
                    interval = parts[1]
                    await self.subscribe_klines(symbols, [interval])

    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """Get latest ticker data"""
        return self.tickers.get(symbol)

    def get_orderbook(self, symbol: str) -> Optional[Dict]:
        """Get latest orderbook data"""
        if symbol in self.orderbooks:
            return {
                'symbol': symbol,
                'bids': sorted(self.orderbooks[symbol]['bids'].items(), reverse=True)[:25],
                'asks': sorted(self.orderbooks[symbol]['asks'].items())[:25]
            }
        return None

    def get_stats(self) -> Dict:
        """Get WebSocket statistics"""
        return {
            'connected': self.is_connected,
            'messages_received': self.messages_received,
            'subscribed_symbols': len(self.subscribed_symbols),
            'latency_ms': self.latency_ms,
            'last_message': self.last_message_time
        }


# Example usage
if __name__ == '__main__':
    async def main():
        # Initialize WebSocket
        ws = BybitWebSocket(testnet=True)

        # Connect
        await ws.connect()

        # Subscribe to data
        symbols = ['BTCUSDT', 'ETHUSDT']
        await ws.subscribe_ticker(symbols)
        await ws.subscribe_orderbook(symbols)
        await ws.subscribe_trades(symbols)
        await ws.subscribe_klines(symbols, ['1', '5'])

        # Wait for data
        await asyncio.sleep(10)

        # Print stats
        stats = ws.get_stats()
        print(f"\n📊 WebSocket Stats:")
        print(f"   Messages: {stats['messages_received']}")
        print(f"   Latency: {stats['latency_ms']:.2f}ms")
        print(f"   Symbols: {stats['subscribed_symbols']}")

        # Print ticker
        for symbol in symbols:
            ticker = ws.get_ticker(symbol)
            if ticker:
                print(f"\n💰 {symbol}: ${ticker['last_price']:,.2f}")

        # Disconnect
        await ws.disconnect()

    asyncio.run(main())
