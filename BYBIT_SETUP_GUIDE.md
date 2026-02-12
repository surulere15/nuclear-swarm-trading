# 🚀 Bybit Testnet Setup Guide for Nuclear Swarm

**Complete setup guide for deploying Nuclear Swarm on Bybit testnet**

---

## 📋 STEP 1: Create Bybit Testnet Account (5 minutes)

### **1.1 Sign Up**
1. Visit: **https://testnet.bybit.com**
2. Click **"Sign Up"** (top right corner)
3. Choose registration method:
   - Email (recommended)
   - Phone number
4. Complete verification
5. Set password (strong password required)

### **1.2 Get Free Test Funds**
1. Log in to your testnet account
2. Go to **Assets** → **Derivatives Account**
3. You should see free testnet USDT (usually 10,000-100,000)
4. If not showing:
   - Click **"Claim Test Coins"** button
   - Wait 1-2 minutes for funds to appear

✅ **You now have free test USDT to trade with!**

---

## 🔑 STEP 2: Create API Keys (5 minutes)

### **2.1 Navigate to API Management**
1. Click your **profile icon** (top right)
2. Select **"API"** from dropdown menu
3. Or go directly to: https://testnet.bybit.com/app/user/api-management

### **2.2 Create New API Key**
1. Click **"Create New Key"**
2. Choose **"System-generated API Keys"**
3. Fill in details:
   ```
   API Key Name: Nuclear Swarm Trading
   ```

### **2.3 Set Permissions**
✅ **Enable these permissions:**
- **Contract Trading** (REQUIRED)
  - Read
  - Trade
- **Position** (REQUIRED)
  - Read
- **Wallet** (REQUIRED)
  - Read

❌ **DO NOT enable:**
- Withdrawal
- Transfer
- Sub-account

### **2.4 IP Restriction (Optional)**
- **Option A:** Leave empty (allow all IPs) - easier for testing
- **Option B:** Add your IP address - more secure

### **2.5 Save Your Keys**
⚠️ **CRITICAL - SHOWN ONLY ONCE!**

After clicking **"Confirm"**, you'll see:
```
API Key:    aBc123...xyz789
API Secret: XyZ456...abc123
```

**COPY AND SAVE BOTH IMMEDIATELY!**

Save them in a secure location:
- Password manager (recommended)
- Encrypted file
- Paper backup

**You CANNOT view the secret again!**

---

## 💻 STEP 3: Configure Nuclear Swarm

### **3.1 Create Config File**

In your `nuclear-swarm-trading` directory, create a file called `config.py`:

```python
"""
Bybit Configuration for Nuclear Swarm
TESTNET credentials
"""

# Bybit API Credentials (TESTNET)
BYBIT_API_KEY = "YOUR_API_KEY_HERE"        # Paste your API key
BYBIT_API_SECRET = "YOUR_API_SECRET_HERE"  # Paste your API secret

# Mode
TESTNET = True  # ALWAYS True for testnet

# Trading Parameters
INITIAL_CAPITAL = 500  # USDT to deploy
MAX_POSITIONS = 100    # Concurrent positions
POSITION_SIZE_MIN = 0.005  # 0.5% per position
POSITION_SIZE_MAX = 0.03   # 3.0% per position

# Symbols to Trade (20 pairs)
SYMBOLS = [
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT',
    'ARBUSDT', 'MATICUSDT', 'AVAXUSDT', 'LINKUSDT',
    'UNIUSDT', 'ATOMUSDT', 'DOTUSDT', 'ADAUSDT',
    'XRPUSDT', 'DOGEUSDT', 'LTCUSDT', 'BCHUSDT',
    'ETCUSDT', 'FILUSDT', 'NEARUSDT', 'APTUSDT'
]

# Strategy Leverage Settings
LEVERAGE = {
    'hf_scalping': 20,
    'momentum': 15,
    'stat_arb': 12,
    'funding_arb': 10,
    'grid': 8
}

# Risk Management
CIRCUIT_BREAKER_DAILY_LOSS = 0.10  # 10%
CIRCUIT_BREAKER_TOTAL_DRAWDOWN = 0.15  # 15%
CIRCUIT_BREAKER_STRATEGY_LOSS = 0.05  # 5%

# Deployment
DURATION_HOURS = 24  # How long to run
SCAN_INTERVAL_SECONDS = 10  # Opportunity scanning frequency
```

### **3.2 Add Your API Keys**

Edit `config.py` and replace:
```python
BYBIT_API_KEY = "aBc123...xyz789"        # Your actual key
BYBIT_API_SECRET = "XyZ456...abc123"     # Your actual secret
```

⚠️ **IMPORTANT:** Never commit config.py to git! It's in .gitignore

---

## ✅ STEP 4: Test Connection

### **4.1 Run Connection Test**

```bash
cd nuclear-swarm-trading
python3 bybit_connector.py
```

**Expected Output:**
```
✅ Bybit Connector initialized (TESTNET)
🔍 Testing Bybit connection...
✅ Public API working (BTC price: $XX,XXX.XX)
✅ Authentication working (Balance: $10,000.00 USDT)
✅ Bybit connection test PASSED!

🚀 Ready to trade on Bybit testnet!
💰 Account Balance: $10,000.00 USDT
📊 BTC/USDT: $XX,XXX.XX
📈 Active Positions: 0
```

✅ **If you see this, you're ready to deploy!**

❌ **If you see errors:**
- Check API key/secret are correct
- Verify permissions are enabled
- Ensure testnet mode is True
- Check internet connection

---

## 🧪 STEP 5: Test WebSocket (Optional)

### **5.1 Run WebSocket Test**

```bash
python3 bybit_websocket.py
```

**Expected Output:**
```
✅ Bybit WebSocket initialized (TESTNET)
✅ Connected to Bybit WebSocket
📊 Subscribed to ticker: BTCUSDT
📊 Subscribed to ticker: ETHUSDT
📖 Subscribed to orderbook: BTCUSDT
📖 Subscribed to orderbook: ETHUSDT
💱 Subscribed to trades: BTCUSDT
💱 Subscribed to trades: ETHUSDT
🕯️ Subscribed to 1m klines: BTCUSDT
🕯️ Subscribed to 5m klines: BTCUSDT

📊 WebSocket Stats:
   Messages: 1,234
   Latency: 45.67ms
   Symbols: 2

💰 BTCUSDT: $XX,XXX.XX
💰 ETHUSDT: $X,XXX.XX
```

✅ **WebSocket working perfectly!**

---

## 🚀 STEP 6: Deploy Nuclear Swarm

### **6.1 Run Deployment**

```bash
python3 DEPLOY_NUCLEAR_SWARM.py
```

### **6.2 Confirm Deployment**

When prompted, type:
```
DEPLOY
```

### **6.3 Watch It Run!**

You'll see:
```
════════════════════════════════════════════════════════════════
🚀 NUCLEAR SWARM TRADING - REAL-TIME DASHBOARD (BYBIT TESTNET)
Target: $500 → $2,872 in 30 days (+474%)
════════════════════════════════════════════════════════════════

💰 CAPITAL (Liquid Flow):
   Total:      $     512.50
   Available:  $     152.50
   Deployed:   $     360.00 (70.2%)
   Total P&L:  $     +12.50 (+2.50%)
   Daily P&L:  $     +8.30 (+1.66%)

🐝 SWARM STATUS:
   Active Positions:   68 / 100
   Utilization:        68.0%
   Total Opened:       136
   Total Closed:        68
   Win Rate:           67.6%

🔍 OPPORTUNITY COVERAGE:
   Symbols Scanned:     20
   Strategies Active:   5
   Total Combinations:  240
   Opportunities Found: 68 / 240 scanned
   Acceptance Rate:     28.3%
```

---

## 📊 STEP 7: Monitor Performance

### **7.1 Dashboard Updates**
- Dashboard refreshes every 2 seconds
- Watch P&L change in real-time
- Monitor win rate
- Track position count

### **7.2 Check Bybit Testnet**
Visit https://testnet.bybit.com to see:
- Open positions
- Order history
- P&L charts
- Account balance changes

### **7.3 Review Logs**
All activity is logged:
```
nuclear_swarm_YYYYMMDD_HHMMSS.log
```

---

## 🎯 Success Criteria (7 Days)

Run the system for 7 days on testnet and validate:

✅ **Performance Targets:**
- Average daily return: ≥6.0%
- Win rate: ≥65%
- Max drawdown: <15%
- System uptime: >95%

✅ **Technical Validation:**
- No critical errors
- Circuit breakers working
- All strategies executing
- WebSocket stable (<100ms latency)

✅ **Risk Management:**
- Position limits respected
- Stop losses executing
- Take profits hitting
- Emergency stops functional

---

## 🔄 STEP 8: After Testnet Success

### **Option A: Deploy with $100 Live**
Once testnet is successful:
1. Create live Bybit account
2. Get live API keys
3. Change config: `TESTNET = False`
4. Deploy with `INITIAL_CAPITAL = 100`
5. Run for 7 days
6. Target: $374 profit (+374%)

### **Option B: Scale to $500 Live**
After $100 success:
1. Increase capital: `INITIAL_CAPITAL = 500`
2. Deploy full Nuclear Swarm
3. Run for 30 days
4. Target: $2,872 (+474%)

---

## ⚠️ Important Reminders

### **Security:**
- ✅ Keep API keys private
- ✅ Never share API secret
- ✅ Don't commit config.py to git
- ✅ Use testnet first

### **Trading:**
- ✅ Testnet ≠ Live (different liquidity)
- ✅ Monitor constantly during testing
- ✅ Start small when going live
- ✅ Only risk what you can afford to lose

### **System:**
- ✅ Keep computer running during deployment
- ✅ Stable internet required
- ✅ Don't close terminal
- ✅ Check logs regularly

---

## 🆘 Troubleshooting

### **"Failed to authenticate"**
- Check API key/secret are correct
- Verify permissions enabled
- Ensure using testnet keys for testnet

### **"Insufficient balance"**
- Claim test coins on Bybit testnet
- Reduce INITIAL_CAPITAL in config
- Check derivatives account (not spot)

### **"Position limit exceeded"**
- Reduce MAX_POSITIONS in config
- Some symbols may have limits
- Check Bybit position limits

### **"WebSocket disconnected"**
- Check internet connection
- System auto-reconnects
- Review logs for details

### **"Circuit breaker triggered"**
- Daily loss >10% - system protecting capital
- Review strategy performance
- Adjust parameters if needed
- This is working as designed!

---

## 📞 Ready?

### **Checklist:**
- [ ] Bybit testnet account created
- [ ] Test USDT received
- [ ] API keys created and saved
- [ ] config.py created with keys
- [ ] Connection test passed
- [ ] WebSocket test passed (optional)
- [ ] Ready to deploy!

### **Deploy Now:**
```bash
cd nuclear-swarm-trading
python3 DEPLOY_NUCLEAR_SWARM.py
```

**Type when prompted:** `DEPLOY`

---

## 🌊 THE NUCLEAR SWARM IS READY FOR BYBIT!

**Testnet First → $100 Live → $500 Full Scale**

**Let's achieve that 474% monthly target! 🚀💰**

---

**Last Updated:** February 12, 2026
**Platform:** Bybit Testnet
**Status:** ✅ Ready to Deploy
