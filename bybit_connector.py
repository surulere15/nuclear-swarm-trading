"""
Bybit API Connector for Nuclear Swarm Trading System
Handles all Bybit REST API interactions
"""

import hashlib
import hmac
import time
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class BybitConnector:
    """Bybit API connector with full trading capabilities"""

    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initialize Bybit connector

        Args:
            api_key: Bybit API key
            api_secret: Bybit API secret
            testnet: Use testnet (True) or live (False)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet

        # API endpoints
        if testnet:
            self.base_url = "https://api-testnet.bybit.com"
        else:
            self.base_url = "https://api.bybit.com"

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 500ms between requests

        print(f"✅ Bybit Connector initialized ({'TESTNET' if testnet else 'LIVE'})")

    def _generate_signature(self, params: Dict) -> str:
        """Generate HMAC SHA256 signature for Bybit API"""
        # Sort parameters alphabetically
        sorted_params = sorted(params.items())
        param_string = '&'.join([f"{k}={v}" for k, v in sorted_params])

        # Generate signature
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            param_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return signature

    def _make_request(self, method: str, endpoint: str, params: Dict = None, signed: bool = True) -> Dict:
        """
        Make HTTP request to Bybit API

        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint
            params: Request parameters
            signed: Whether request needs signature

        Returns:
            API response as dict
        """
        if params is None:
            params = {}

        # Add timestamp and API key for signed requests
        if signed:
            timestamp = str(int(time.time() * 1000))
            params['api_key'] = self.api_key
            params['timestamp'] = timestamp

            # Generate signature
            params['sign'] = self._generate_signature(params)

        # Rate limiting
        time_since_last_request = time.time() - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)

        # Make request
        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, params=params, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=params, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")

            self.last_request_time = time.time()

            # Parse response
            data = response.json()

            if data.get('ret_code') != 0 and data.get('retCode') != 0:
                print(f"❌ Bybit API Error: {data.get('ret_msg') or data.get('retMsg')}")
                return None

            return data

        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return None

    def get_account_balance(self) -> Optional[Dict]:
        """Get account balance"""
        endpoint = "/v2/private/wallet/balance"
        params = {'coin': 'USDT'}

        response = self._make_request("GET", endpoint, params)
        if response and response.get('result'):
            balance_data = response['result'].get('USDT', {})
            return {
                'total_balance': float(balance_data.get('wallet_balance', 0)),
                'available_balance': float(balance_data.get('available_balance', 0)),
                'used_margin': float(balance_data.get('used_margin', 0))
            }
        return None

    def get_positions(self, symbol: str = None) -> List[Dict]:
        """
        Get current positions

        Args:
            symbol: Specific symbol (e.g., 'BTCUSDT') or None for all

        Returns:
            List of position dictionaries
        """
        endpoint = "/v2/private/position/list"
        params = {}
        if symbol:
            params['symbol'] = symbol

        response = self._make_request("GET", endpoint, params)
        if response and response.get('result'):
            positions = []
            for pos in response['result']:
                if float(pos.get('size', 0)) > 0:
                    positions.append({
                        'symbol': pos['symbol'],
                        'side': pos['side'],
                        'size': float(pos['size']),
                        'entry_price': float(pos['entry_price']),
                        'leverage': float(pos['leverage']),
                        'unrealized_pnl': float(pos.get('unrealised_pnl', 0)),
                        'liquidation_price': float(pos.get('liq_price', 0))
                    })
            return positions
        return []

    def place_market_order(
        self,
        symbol: str,
        side: str,
        qty: float,
        reduce_only: bool = False,
        stop_loss: float = None,
        take_profit: float = None
    ) -> Optional[Dict]:
        """
        Place market order

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'Buy' or 'Sell'
            qty: Quantity in contracts
            reduce_only: Close position only
            stop_loss: Stop loss price
            take_profit: Take profit price

        Returns:
            Order response dict
        """
        endpoint = "/v2/private/order/create"

        params = {
            'symbol': symbol,
            'side': side,
            'order_type': 'Market',
            'qty': qty,
            'time_in_force': 'ImmediateOrCancel',
            'reduce_only': reduce_only,
            'close_on_trigger': False
        }

        if stop_loss:
            params['stop_loss'] = stop_loss
        if take_profit:
            params['take_profit'] = take_profit

        response = self._make_request("POST", endpoint, params)

        if response and response.get('result'):
            result = response['result']
            return {
                'order_id': result.get('order_id'),
                'symbol': symbol,
                'side': side,
                'qty': qty,
                'status': 'submitted'
            }
        return None

    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """
        Set leverage for a symbol

        Args:
            symbol: Trading pair
            leverage: Leverage (1-100)

        Returns:
            Success status
        """
        endpoint = "/v2/private/position/leverage/save"

        params = {
            'symbol': symbol,
            'buy_leverage': leverage,
            'sell_leverage': leverage
        }

        response = self._make_request("POST", endpoint, params)
        return response is not None

    def close_position(self, symbol: str, side: str) -> Optional[Dict]:
        """
        Close entire position for a symbol

        Args:
            symbol: Trading pair
            side: Position side to close ('Buy' closes short, 'Sell' closes long)

        Returns:
            Order response dict
        """
        # Get current position size
        positions = self.get_positions(symbol)
        if not positions:
            return None

        for pos in positions:
            if pos['symbol'] == symbol:
                # Close position with reduce_only market order
                close_side = 'Sell' if pos['side'] == 'Buy' else 'Buy'
                return self.place_market_order(
                    symbol=symbol,
                    side=close_side,
                    qty=pos['size'],
                    reduce_only=True
                )

        return None

    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """
        Get latest ticker data

        Args:
            symbol: Trading pair

        Returns:
            Ticker data dict
        """
        endpoint = "/v2/public/tickers"
        params = {'symbol': symbol}

        response = self._make_request("GET", endpoint, params, signed=False)

        if response and response.get('result'):
            result = response['result'][0] if isinstance(response['result'], list) else response['result']
            return {
                'symbol': symbol,
                'last_price': float(result.get('last_price', 0)),
                'bid': float(result.get('bid_price', 0)),
                'ask': float(result.get('ask_price', 0)),
                'volume_24h': float(result.get('volume_24h', 0)),
                'price_change_pct': float(result.get('price_24h_pcnt', 0)) * 100
            }
        return None

    def get_funding_rate(self, symbol: str) -> Optional[Dict]:
        """
        Get current and predicted funding rate

        Args:
            symbol: Trading pair

        Returns:
            Funding rate data
        """
        endpoint = "/v2/public/tickers"
        params = {'symbol': symbol}

        response = self._make_request("GET", endpoint, params, signed=False)

        if response and response.get('result'):
            result = response['result'][0] if isinstance(response['result'], list) else response['result']
            return {
                'symbol': symbol,
                'funding_rate': float(result.get('funding_rate', 0)),
                'predicted_funding_rate': float(result.get('predicted_funding_rate', 0)),
                'next_funding_time': result.get('next_funding_time', '')
            }
        return None

    def test_connection(self) -> bool:
        """Test API connection and credentials"""
        print("\n🔍 Testing Bybit connection...")

        # Test public endpoint (no auth)
        ticker = self.get_ticker('BTCUSDT')
        if not ticker:
            print("❌ Failed to connect to Bybit API")
            return False
        print(f"✅ Public API working (BTC price: ${ticker['last_price']:,.2f})")

        # Test private endpoint (with auth)
        balance = self.get_account_balance()
        if not balance:
            print("❌ Failed to authenticate (check API key/secret)")
            return False
        print(f"✅ Authentication working (Balance: ${balance['total_balance']:,.2f} USDT)")

        print("✅ Bybit connection test PASSED!\n")
        return True


# Example usage
if __name__ == '__main__':
    # TESTNET credentials (replace with your keys)
    API_KEY = "YOUR_TESTNET_API_KEY"
    API_SECRET = "YOUR_TESTNET_API_SECRET"

    # Initialize connector
    bybit = BybitConnector(api_key=API_KEY, api_secret=API_SECRET, testnet=True)

    # Test connection
    if bybit.test_connection():
        print("🚀 Ready to trade on Bybit testnet!")

        # Get account info
        balance = bybit.get_account_balance()
        print(f"\n💰 Account Balance: ${balance['total_balance']:,.2f} USDT")

        # Get BTC price
        ticker = bybit.get_ticker('BTCUSDT')
        print(f"📊 BTC/USDT: ${ticker['last_price']:,.2f}")

        # Get positions
        positions = bybit.get_positions()
        print(f"📈 Active Positions: {len(positions)}")
