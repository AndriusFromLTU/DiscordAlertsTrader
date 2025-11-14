# DiscordAlertsTrader Repository Summary

This is an **automated trading bot** that monitors Discord channels for trading alerts from analysts and executes trades through various brokerage APIs. It's designed to parse, track, and optionally auto-trade options and stocks based on Discord messages.

---

## Main Components & Classes

### 1. DiscordBot (`discord_bot.py`)
**Purpose:** Core Discord integration - monitors channels and processes messages in real-time

**Responsibilities:**
- Connects to Discord using user token and listens to specified channels
- Parses incoming trade alert messages
- Routes alerts to `AlertsTracker` and `AlertsTrader`
- Runs background thread for live quote tracking
- Manages message history in CSV files

---

### 2. AlertsTrader (`alerts_trader.py`)
**Purpose:** Executes actual trades through brokerage APIs

**Responsibilities:**
- Places BTO/STO (Buy/Sell to Open) orders with brokerages
- Manages STC/BTC (Sell/Buy to Close) exit orders
- Handles profit target (PT), stop loss (SL), and trailing stop orders
- Tracks trader's portfolio (positions actually traded)
- Updates order status and manages position averaging
- Generates trader performance portfolio CSV

---

### 3. AlertsTracker (`alerts_tracker.py`)
**Purpose:** Tracks analyst alerts without executing trades (observational tracking)

**Responsibilities:**
- Records all BTO/STC alerts from analysts
- Calculates hypothetical P&L for analyst portfolios
- Tracks alerts with live market prices
- Handles position averaging for alerts
- Generates analyst performance portfolio CSV
- Used for evaluating analyst performance before auto-trading

---

### 4. MessageParser (`message_parser.py`)
**Purpose:** Natural language parsing of trading alerts

**Responsibilities:**
- Extracts trade details from unstructured Discord messages
- Parses: action (BTO/STC), ticker, quantity, price, strike/expiration (options)
- Identifies profit targets (PT1, PT2, PT3), stop losses (SL)
- Handles exit updates, averaging alerts, trailing stops
- Converts option symbols to standard format (e.g., `AAPL_092623C150`)

---

### 5. GUI (`gui.py`)
**Purpose:** User interface built with ttkbootstrap/tkinter

**Responsibilities:**
- Displays analyst and trader portfolios with live P&L
- Shows message history for each channel
- Manual alert input/triggering
- Portfolio statistics and performance metrics
- Order management (check status, cancel orders)
- Configuration for auto-trading vs. manual mode

---

### 6. Configurator (`configurator.py`)
**Purpose:** Configuration management

**Responsibilities:**
- Loads `config.ini` settings (Discord token, channel IDs, brokerage keys)
- Defines portfolio column schemas
- Updates legacy portfolio formats
- Manages file paths for data/portfolios

---

### 7. ServerAlertFormatting (`server_alert_formatting.py`)
**Purpose:** Custom parsers for different Discord servers/analysts

**Responsibilities:**
- Contains 20+ custom formatting functions for specific analysts
- Handles embedded Discord messages
- Normalizes varied alert formats to standard format
- Server-specific logic (e.g., TradeProElite, Supreme Alerts, Bear alerts)

---

### 8. Brokerage Adapters (`brokerages/`)
**Purpose:** API integrations for trade execution

**Main Classes:**
- **BaseBroker** (abstract): Defines interface for all brokerages
- **TDA**: TD Ameritrade API
- **SW** (Schwab): Charles Schwab API
- **TS**: TradeStation API
- **weBull**: WeBull API
- **eTrade**: E*TRADE API
- **IBKR**: Interactive Brokers API

**Responsibilities:**
- Place/cancel orders
- Get quotes, positions, order status
- Account management

---

### 9. CalcStrat (`calc_strat.py`)
**Purpose:** Backtesting and strategy analysis

**Responsibilities:**
- Calculates historical returns from saved quotes
- Tests different exit strategies (PT, SL, trailing stops)
- Filters trades by date, price, DTE, author
- Simulates portfolio performance with various parameters

---

### 10. PortSim (`port_sim.py`)
**Purpose:** Portfolio simulation and historical data retrieval

**Responsibilities:**
- Fetches historical option quotes (via ThetaData API)
- Simulates trade execution timing
- Calculates ROI with different exit rules
- Trailing stop calculations

---

## Workflow

1. **DiscordBot** monitors channels → detects alert message
2. **ServerAlertFormatting** normalizes message format
3. **MessageParser** extracts trade details
4. **AlertsTracker** logs alert and calculates hypothetical P&L
5. **AlertsTrader** (if enabled) executes trade via brokerage API
6. **GUI** displays portfolios with live quotes and statistics
7. **CalcStrat/PortSim** used for backtesting and strategy optimization

---

## Key Features

- **Dual Tracking System**: Track analyst alerts (passive) and actual trades (active) separately
- **Multiple Brokerage Support**: Works with TD Ameritrade, Schwab, TradeStation, WeBull, E*TRADE, and Interactive Brokers
- **Live Quote Tracking**: Continuous price updates for open positions
- **Exit Strategy Management**: Supports multiple profit targets, stop losses, and trailing stops
- **Backtesting Framework**: Test strategies on historical data before live trading
- **Customizable Parsing**: 20+ analyst-specific message formatters
- **GUI Dashboard**: Real-time portfolio monitoring and manual trade controls

---

This system enables automated trading based on Discord alerts while providing full transparency into analyst performance, trade execution, and P&L tracking.
