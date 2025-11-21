# 2025-11-20 - Meridian Trading Architecture (Current State)

**Date:** 2025-11-20  
**Status:** ⚠️ **IN DEVELOPMENT** (Core Complete, Self-Learning Pending)  
**Purpose:** Comprehensive architectural overview of meridian-trading domain adapter

---

## Executive Summary

**Meridian Trading** is a **domain-specific adapter** that uses Meridian Core to orchestrate AI models for trading decisions. It implements Larry Williams' proven trading strategies (Williams %R, ATR-based stops, risk management) with AI-powered analysis, signal generation, and risk management.

**Key Features:**
- **Trading Strategies**: Williams %R Reversal, TDOM (Time of Day/Month), COT Analysis
- **Risk Management**: 2% per trade, 6% portfolio maximum, ATR-based stops
- **AI-Powered Analysis**: Uses Meridian Core to analyze market conditions and generate signals
- **Market Indicators**: Williams %R, ATR (Average True Range), COT positioning
- **Market Scanner**: Multi-market scanning and signal detection
- **Backtesting**: Test strategies on historical data

**Key Principle:** Meridian Trading extends Meridian Core with trading-specific logic, strategies, and workflows.

---

## 1. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        MERIDIAN-TRADING                                       │
│                     (Trading Domain Adapter)                                  │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  APPLICATION LAYER                                                            │
│  (CLI, API, User Interface)                                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│  • CLI commands (trading, scanner, backtest, etc.)                            │
│  • Python API (TradingEngine)                                                 │
│  • Integration points                                                         │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  TRADING ENGINE LAYER                                                          │
│  (Trading Orchestration)                                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              TradingEngine                                         │      │
│  │  • Main orchestrator for trading tasks                            │      │
│  │  • Market analysis                                                │      │
│  │  • Signal generation                                              │      │
│  │  • Strategy execution                                             │      │
│  │  • Position management                                            │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              TradingSystem                                          │      │
│  │  • Executes trades                                                 │      │
│  │  • Manages positions                                              │      │
│  │  • Calculates performance metrics                                 │      │
│  └────────────────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  STRATEGY LAYER                                                                │
│  (Trading Strategies)                                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              StrategyBase (Abstract)                               │      │
│  │  • Abstract base class for strategies                              │      │
│  │  • Common strategy interface                                       │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
│  Implementations:                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │  • WilliamsRStrategy → Williams %R reversal strategy               │      │
│  │  • CombinedTimingStrategy → TDOM + TDOW + TDOY timing              │      │
│  │  • COTStrategy → Commitment of Traders analysis                    │      │
│  │  • ... (extensible)                                                │      │
│  └────────────────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  INDICATOR LAYER                                                               │
│  (Technical Indicators)                                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              Technical Indicators                                  │      │
│  │  • WilliamsR → Williams %R indicator                              │      │
│  │  • ATR → Average True Range                                        │      │
│  │  • COT → Commitment of Traders positioning                         │      │
│  │  • ... (extensible)                                                │      │
│  └────────────────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  RISK MANAGEMENT LAYER                                                         │
│  (Risk Control)                                                                │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              RiskManager                                           │      │
│  │  • 2% maximum risk per trade                                      │      │
│  │  • 6% maximum portfolio risk                                      │      │
│  │  • ATR-based stop losses                                          │      │
│  │  • Maximum 3 concurrent positions                                 │      │
│  │  • Guaranteed stops                                               │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              CorrelationManager                                    │      │
│  │  • Position correlation tracking                                   │      │
│  │  • Diversification enforcement                                    │      │
│  │  • Correlation-based risk limits                                   │      │
│  └────────────────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  MARKET DATA LAYER                                                             │
│  (Market Data & Analysis)                                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              MarketDataProvider                                    │      │
│  │  • Market data retrieval (OHLCV)                                  │      │
│  │  • COT data retrieval                                              │      │
│  │  • Historical data access                                          │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              MarketScanner                                         │      │
│  │  • Multi-market scanning                                          │      │
│  │  • Signal detection                                                │      │
│  │  • Pattern recognition                                             │      │
│  └────────────────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  MERIDIAN CORE ADAPTER LAYER                                                   │
│  (Bridge to meridian-core)                                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              OrchestratorBridge                                    │      │
│  │  • Bridge between meridian-trading and meridian-core               │      │
│  │  • Connector initialization                                        │      │
│  │  • Task creation and dispatch                                      │      │
│  │  • AI-powered analysis                                             │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
│  Uses meridian-core components:                                               │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │  • AIOrchestrator → Multi-AI coordination                          │      │
│  │  • Connectors → AI provider integration                            │      │
│  │  • VotingManager → Multi-AI consensus                              │      │
│  │  • CredentialStore → Unified credential management                 │      │
│  └────────────────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  LEARNING LAYER ⚠️ (PLANNED)                                                   │
│  (Self-Learning & Pattern Detection)                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              LearningBridge (PLACEHOLDER)                          │      │
│  │  ⚠️  Currently only bridge.py exists                                │      │
│  │  ❌ TradingLearningEngine NOT IMPLEMENTED                           │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              TradingLearningEngine (PLANNED)                       │      │
│  │  (extends LearningEngine from meridian-core)                       │      │
│  │                                                                     │      │
│  │  PLANNED Methods:                                                   │      │
│  │  • analyze_performance() → Trading metrics                         │      │
│  │    - Sharpe ratio, win rate, profit factor                         │      │
│  │    - Drawdown analysis                                             │      │
│  │    - Strategy performance                                          │      │
│  │                                                                     │      │
│  │  • detect_patterns() → Trading patterns                            │      │
│  │    - TDOM patterns (time-of-day/month)                             │      │
│  │    - Losing streaks                                                │      │
│  │    - Strategy effectiveness                                        │      │
│  │                                                                     │      │
│  │  • generate_hypothesis() → Improvement hypotheses                  │      │
│  │    - "Avoid trading 2-4 PM"                                       │      │
│  │    - "Adjust strategy X parameters"                                │      │
│  │    - "Review risk management for strategy Y"                       │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              TradingPatternDetector (PLANNED)                      │      │
│  │  ❌ NOT IMPLEMENTED                                                 │      │
│  │  • TDOM pattern detection                                           │      │
│  │  • Losing streak detection                                          │      │
│  │  • Strategy-specific patterns                                       │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              ProposalManager (from meridian-core)                   │      │
│  │  • Would use shared proposal database                               │      │
│  │  • Would store proposals in: logs/proposals.db                      │      │
│  │  • Status tracking: pending → approved → implemented               │      │
│  └────────────────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  BROKER INTEGRATION LAYER ⚠️ (BLOCKED)                                         │
│  (Order Execution)                                                            │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              IGConnector (from meridian-core) ⚠️ BLOCKED            │      │
│  │  • IG Markets API integration                                      │      │
│  │  • Order execution                                                 │      │
│  │  • Position management                                             │      │
│  │  • Account management                                              │      │
│  │  ⚠️  Currently blocked, structure ready                            │      │
│  └────────────────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Components

### 2.1 Trading Engine

#### TradingEngine
```
Location: src/meridian_trading/core/trading_engine.py
Status: ⚠️ Structure exists, implementation in progress

Purpose: Main orchestrator for trading tasks

Key Features:
• Market analysis
• Signal generation
• Strategy execution
• Position management
• Performance tracking

Methods:
• analyze_market(symbol, timeframe)
• generate_signals(strategy, market_data)
• execute_strategy(strategy, signals)
• manage_positions()
• calculate_performance()
```

#### TradingSystem
```
Location: src/meridian_trading/core/trading_system.py
Status: ⚠️ Structure exists, implementation in progress

Purpose: Executes trades and manages positions

Key Features:
• Trade execution
• Position management
• Performance metrics calculation

Methods:
• execute_trade(signal, risk_params)
• manage_position(position)
• calculate_metrics(period)
```

### 2.2 Strategy Components

#### StrategyBase (Abstract)
```
Location: src/meridian_trading/strategies/base.py
Purpose: Abstract base class for trading strategies

Abstract Methods:
• generate_signals(market_data) → List[Signal]
• backtest(start_date, end_date) → BacktestResult
• calculate_position_size(signal, account_balance) → float

Generic Methods:
• validate_signals(signals) → List[Signal]
• calculate_stop_loss(signal, atr) → float
```

#### WilliamsRStrategy
```
Location: src/meridian_trading/strategies/williams_r_strategy.py
Status: ✅ Implemented

Purpose: Williams %R reversal strategy

Features:
• Williams %R indicator calculation
• Reversal signal detection
• Entry/exit logic
• Stop loss calculation (ATR-based)
• Backtesting support

Methods:
• calculate_williams_r(high, low, close, period=14)
• generate_signals(market_data)
• backtest(start_date, end_date)
```

#### CombinedTimingStrategy
```
Location: src/meridian_trading/strategies/combined_timing_strategy.py
Status: ✅ Implemented

Purpose: TDOM + TDOW + TDOY timing strategy

Features:
• Time-of-day (TDOM) filtering
• Time-of-week (TDOW) filtering
• Time-of-year (TDOY) filtering
• Combined timing signals
• Entry/exit logic

Methods:
• filter_by_timing(trade_time)
• generate_signals(market_data)
• backtest(start_date, end_date)
```

#### COTStrategy
```
Location: src/meridian_trading/strategies/cot_strategy.py
Status: ⚠️ Planned

Purpose: Commitment of Traders analysis strategy

Features:
• COT data retrieval
• Positioning analysis
• Signal generation
• Entry/exit logic
```

### 2.3 Indicator Components

#### WilliamsR
```
Location: src/meridian_trading/indicators/williams_r.py
Status: ✅ Implemented

Purpose: Williams %R technical indicator

Features:
• Williams %R calculation
• Overbought/oversold levels
• Signal generation

Methods:
• calculate(high, low, close, period=14)
• is_overbought(value, threshold=-20)
• is_oversold(value, threshold=-80)
```

#### ATR
```
Location: src/meridian_trading/indicators/atr.py
Status: ✅ Implemented

Purpose: Average True Range indicator

Features:
• ATR calculation
• Volatility measurement
• Stop loss calculation

Methods:
• calculate(high, low, close, period=14)
• calculate_stop_loss(entry_price, atr, multiplier=2.0)
```

#### COT
```
Location: src/meridian_trading/indicators/cot.py
Status: ⚠️ Planned

Purpose: Commitment of Traders data analysis

Features:
• COT data retrieval
• Positioning analysis
• Signal generation
```

### 2.4 Risk Management Components

#### RiskManager
```
Location: src/meridian_trading/risk/risk_manager.py
Status: ✅ Implemented

Purpose: Risk management enforcement

Key Features:
• 2% maximum risk per trade
• 6% maximum portfolio risk
• ATR-based stop losses
• Maximum 3 concurrent positions
• Guaranteed stops

Methods:
• calculate_position_size(signal, account_balance, risk_pct=0.02)
• validate_trade(signal, current_positions) → bool
• calculate_portfolio_risk(positions) → float
• enforce_risk_limits(trade, positions) → Trade
```

#### CorrelationManager
```
Location: src/meridian_trading/risk/correlation_manager.py
Status: ✅ Implemented

Purpose: Position correlation tracking

Key Features:
• Position correlation calculation
• Diversification enforcement
• Correlation-based risk limits

Methods:
• calculate_correlation(symbol1, symbol2, period=20)
• validate_diversification(positions) → bool
• enforce_correlation_limits(trade, positions) → Trade
```

### 2.5 Market Data Components

#### MarketDataProvider
```
Location: src/meridian_trading/data/market_data_provider.py
Status: ⚠️ Structure exists, implementation in progress

Purpose: Market data retrieval

Features:
• OHLCV data retrieval
• COT data retrieval
• Historical data access
• Real-time data updates

Methods:
• get_ohlcv(symbol, timeframe, start_date, end_date)
• get_cot_data(symbol, start_date, end_date)
• get_latest_data(symbol)
```

#### MarketScanner
```
Location: src/meridian_trading/scanner/market_scanner.py
Status: ⚠️ Planned

Purpose: Multi-market scanning and signal detection

Features:
• Multi-market scanning
• Signal detection
• Pattern recognition
• Market filtering

Methods:
• scan_markets(strategies, markets)
• detect_signals(market_data, strategies)
• filter_markets(criteria)
```

### 2.6 Meridian Core Integration

#### OrchestratorBridge
```
Location: src/meridian_trading/adapters/orchestrator_bridge.py
Status: ✅ Implemented

Purpose: Bridge between meridian-trading and meridian-core

Features:
• Connector initialization
• Task creation and dispatch
• AI-powered analysis
• Multi-AI consensus

Methods:
• initialize_connectors()
• create_analysis_task(market_data, strategy)
• dispatch_to_ai(task)
• synthesize_ai_responses(responses)
```

### 2.7 Learning Components ⚠️ (PLANNED)

#### LearningBridge
```
Location: src/meridian_trading/learning/bridge.py
Status: ⚠️ PLACEHOLDER - Only bridge.py exists

Purpose: Bridge to meridian-core's LearningEngine

Features:
• Imports from meridian_core.learning.learning_engine
• Will extend LearningEngine
• Will implement trading-specific learning
```

#### TradingLearningEngine (PLANNED)
```
Location: src/meridian_trading/learning/trading_learning_engine.py
Status: ❌ NOT IMPLEMENTED

Purpose: Trading-specific learning engine

PLANNED Methods:
• analyze_performance(period_days) → Trading metrics
  - Sharpe ratio, win rate, profit factor
  - Drawdown analysis
  - Strategy performance
  - Position performance

• detect_patterns(trades) → Trading patterns
  - TDOM patterns (time-of-day/month)
  - Losing streaks
  - Strategy effectiveness
  - Market condition patterns

• generate_hypothesis(pattern) → Improvement hypotheses
  - "Avoid trading 2-4 PM"
  - "Adjust strategy X parameters"
  - "Review risk management for strategy Y"
  - "Increase position size for strategy Z"
```

#### TradingPatternDetector (PLANNED)
```
Location: src/meridian_trading/learning/pattern_detector.py
Status: ❌ NOT IMPLEMENTED

Purpose: Trading pattern detection

PLANNED Features:
• TDOM pattern detection
• Losing streak detection
• Strategy-specific patterns
• Market condition patterns
```

---

## 3. Data Flow

### 3.1 Trading Signal Generation Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      TRADING SIGNAL GENERATION FLOW                            │
└──────────────────────────────────────────────────────────────────────────────┘

1. MARKET DATA RETRIEVAL
   ┌──────────────────┐
   │ MarketData       │  → Retrieves OHLCV data
   │ Provider         │  → Retrieves COT data
   │                  │  → Historical data
   └────────┬─────────┘
            │
            ▼
2. INDICATOR CALCULATION
   ┌──────────────────┐
   │ Indicators       │  → Calculates Williams %R
   │                  │  → Calculates ATR
   │                  │  → Analyzes COT data
   └────────┬─────────┘
            │
            ▼
3. SIGNAL GENERATION
   ┌──────────────────┐
   │ Strategy         │  → Generates signals
   │ (Williams %R, etc)│  → Applies timing filters
   │                  │  → Validates signals
   └────────┬─────────┘
            │
            ▼
4. RISK VALIDATION
   ┌──────────────────┐
   │ RiskManager     │  → Validates trade
   │                  │  → Checks position limits
   │                  │  → Enforces risk rules
   └────────┬─────────┘
            │
            ▼
5. AI ANALYSIS (Optional)
   ┌──────────────────┐
   │ Orchestrator     │  → Sends to AI for analysis
   │ Bridge           │  → Multi-AI consensus
   │                  │  → AI-powered insights
   └────────┬─────────┘
            │
            ▼
6. TRADE EXECUTION (if validated)
   ┌──────────────────┐
   │ TradingSystem   │  → Executes trade
   │                  │  → Sets stop loss
   │                  │  → Manages position
   └────────┬─────────┘
            │
            ▼
7. POSITION MANAGEMENT
   ┌──────────────────┐
   │ TradingSystem   │  → Manages position
   │                  │  → Monitors stop loss
   │                  │  → Tracks performance
   └────────┬─────────┘
            │
            ▼
8. PERFORMANCE TRACKING
   ┌──────────────────┐
   │ TradingSystem   │  → Calculates metrics
   │                  │  → Tracks performance
   │                  │  → Records trades
   └──────────────────┘
```

### 3.2 Learning Cycle Flow ⚠️ (PLANNED)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      LEARNING CYCLE FLOW (PLANNED)                            │
└──────────────────────────────────────────────────────────────────────────────┘

1. LEARNING TRIGGER
   ┌──────────────────┐
   │ Learning Cycle   │  → Every 10 trades (configurable)
   │ Manager          │  → Or after 24 hours
   └────────┬─────────┘
            │
            ▼
2. TRADE COLLECTION
   ┌──────────────────┐
   │ TradingSystem   │  → Reads recent trades
   │                  │  → data/positions.db
   └────────┬─────────┘
            │
            ▼
3. PERFORMANCE ANALYSIS
   ┌──────────────────┐
   │ TradingLearning │  → Analyzes recent trades
   │ Engine           │  → Calculates metrics
   │ .analyze_        │  • Sharpe ratio
   │  performance()   │  • Win rate
   │                  │  • Profit factor
   │                  │  • Drawdown
   └────────┬─────────┘
            │
            ▼
4. PATTERN DETECTION
   ┌──────────────────┐
   │ TradingLearning │  → Detects patterns
   │ Engine           │  • TDOM patterns
   │ .detect_         │  • Losing streaks
   │  patterns()      │  • Strategy effectiveness
   │                  │  • Market conditions
   └────────┬─────────┘
            │
            ▼
5. HYPOTHESIS GENERATION
   ┌──────────────────┐
   │ TradingLearning │  → Generates hypotheses
   │ Engine           │  • "Avoid trading 2-4 PM"
   │ .generate_       │  • "Adjust strategy X"
   │  hypothesis()    │  • "Review risk for Y"
   └────────┬─────────┘
            │
            ▼
6. PROPOSAL CREATION
   ┌──────────────────┐
   │ ProposalManager │  → Creates proposals
   │ (from core)      │  → Stores in logs/proposals.db
   │                  │  → Status: pending
   └────────┬─────────┘
            │
            ▼
7. HUMAN REVIEW (Optional)
   ┌──────────────────┐
   │ Human Reviewer  │  → Reviews proposals
   │                  │  → Approves/rejects
   └────────┬─────────┘
            │
            ▼
8. PROPOSAL APPLICATION
   ┌──────────────────┐
   │ ProposalApplicator│ → Applies approved proposals
   │                  │  → Updates strategy parameters
   │                  │  → Updates risk rules
   └──────────────────┘
```

---

## 4. Database Architecture

### 4.1 Main Database (meridian.db)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          meridian.db (SQLite)                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Tables:                                                                      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │  (Basic structure - schema needs verification)                     │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Positions Database (data/positions.db)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      data/positions.db (SQLite)                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Tables:                                                                      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │  positions                                                          │      │
│  │  • id (PK)                                                          │      │
│  │  • symbol (text)                                                    │      │
│  │  • direction (long/short)                                           │      │
│  │  • entry_price (float)                                              │      │
│  │  • stop_loss (float)                                                │      │
│  │  • take_profit (float)                                              │      │
│  │  • position_size (float)                                            │      │
│  │  • risk_amount (float)                                              │      │
│  │  • status (open/closed)                                             │      │
│  │  • entry_time (timestamp)                                           │      │
│  │  • exit_time (timestamp)                                            │      │
│  │  • exit_price (float)                                               │      │
│  │  • pnl (float)                                                      │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Proposal Database (logs/proposals.db - shared with core)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      logs/proposals.db (SQLite)                               │
│              (Shared with meridian-core via ProposalManager)                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Tables:                                                                      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │  proposals                                                          │      │
│  │  • id (PK, UUID)                                                    │      │
│  │  • hypothesis (text)                                                │      │
│  │  • rationale (text)                                                 │      │
│  │  • pattern_id (text)                                                │      │
│  │  • status (pending/approved/rejected/implemented/failed)           │      │
│  │  • performance_data (JSON)                                          │      │
│  │  • created_at                                                       │      │
│  │  • reviewed_at                                                      │      │
│  │  • implemented_at                                                   │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Integration with Meridian Core

### 5.1 How Trading Uses Core

```
meridian-trading
    │
    │ imports from
    ▼
┌─────────────────────────────────────┐
│      meridian-core                 │
│                                     │
│  • AIOrchestrator                   │
│  • Connectors (8 providers)         │
│  • VotingManager                    │
│  • LearningEngine (abstract)        │
│  • ProposalManager                  │
│  • credential_store                 │
└────────────┬────────────────────────┘
             │
             │ implements (PLANNED)
             ▼
┌─────────────────────────────────────┐
│  Trading-Specific Implementation    │
│                                     │
│  ✅ OrchestratorBridge              │
│  ✅ TradingEngine                   │
│  ✅ Strategies                      │
│  ✅ RiskManager                     │
│  ❌ TradingLearningEngine (planned) │
│  ❌ TradingPatternDetector (planned)│
└─────────────────────────────────────┘
```

### 5.2 Credential Management

```
meridian-trading
    │
    │ uses shared credential_store
    ▼
┌─────────────────────────────────────┐
│  meridian_core.utils.credential_   │
│           store                     │
│                                     │
│  Service: meridian-suite            │
│  Credentials:                       │
│    • GROK_API_KEY                   │
│    • GOOGLE_GEMINI_API_KEY          │
│    • ANTHROPIC_API_KEY              │
│    • OPENAI_API_KEY                 │
│    • LOCAL_LLM_URL                  │
│    • IG_USERNAME (trading)          │
│    • IG_PASSWORD (trading)          │
│    • IG_API_KEY (trading)           │
└─────────────────────────────────────┘
```

---

## 6. Configuration Management

### Configuration Files

```
meridian-trading/
├── config.yaml              → Trading configuration
├── allocation_policy.yaml   → Strategy allocation rules
├── risk_config.yaml         → Risk management rules
└── .env (optional)          → Local environment variables
```

### Environment Variables

```
# Credentials (via shared keyring - meridian-suite)
GROK_API_KEY=...
GOOGLE_GEMINI_API_KEY=...
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
LOCAL_LLM_URL=...

# Trading-specific credentials
IG_USERNAME=...
IG_PASSWORD=...
IG_API_KEY=...

# Optional fallback (ALLOW_ENV_FALLBACK=1)
ALLOW_ENV_FALLBACK=0  # Default: disabled for security
```

---

## 7. Risk Management

### Risk Rules

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    RISK MANAGEMENT RULES                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  1. 2% Maximum Risk Per Trade                                                 │
│     • Never risk more than 2% of portfolio on a single trade                  │
│     • Enforced by RiskManager                                                 │
│                                                                               │
│  2. 6% Maximum Portfolio Risk                                                 │
│     • Total open positions never exceed 6% portfolio risk                     │
│     • Enforced by RiskManager                                                 │
│                                                                               │
│  3. ATR-Based Stop Losses                                                     │
│     • Dynamic stops based on market volatility                                │
│     • Calculated using ATR indicator                                          │
│                                                                               │
│  4. Maximum 3 Concurrent Positions                                            │
│     • Prevents over-exposure                                                  │
│     • Enforced by RiskManager                                                 │
│                                                                               │
│  5. Guaranteed Stops                                                          │
│     • All trades use guaranteed stop orders                                   │
│     • Protects against gaps                                                   │
│                                                                               │
│  6. Diversification Enforcement                                               │
│     • Correlation-based position limits                                       │
│     • Enforced by CorrelationManager                                          │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Current Status

### ✅ Completed Components

1. **Strategy System**
   - ✅ StrategyBase (abstract)
   - ✅ WilliamsRStrategy
   - ✅ CombinedTimingStrategy
   - ✅ Strategy interfaces

2. **Indicator System**
   - ✅ WilliamsR indicator
   - ✅ ATR indicator
   - ✅ Indicator calculations

3. **Risk Management**
   - ✅ RiskManager (2%/6% rules)
   - ✅ CorrelationManager
   - ✅ Risk validation

4. **Meridian Core Integration**
   - ✅ OrchestratorBridge
   - ✅ Credential management (shared store)
   - ✅ Connector integration

5. **Infrastructure**
   - ✅ Database models (basic)
   - ✅ Configuration files
   - ✅ Project structure

### ⏳ In Progress / Planned

1. **Trading Engine**
   - ⏳ TradingEngine (structure exists, implementation in progress)
   - ⏳ TradingSystem (structure exists, implementation in progress)

2. **Market Data**
   - ⏳ MarketDataProvider (structure exists, implementation in progress)
   - ⏳ MarketScanner (planned)

3. **Broker Integration**
   - ⏳ IGConnector (from meridian-core) - ⚠️ BLOCKED, structure ready
   - ⏳ Order execution engine (planned)
   - ⏳ Position state management (planned)

4. **Self-Learning System**
   - ❌ TradingLearningEngine (NOT IMPLEMENTED)
   - ❌ TradingPatternDetector (NOT IMPLEMENTED)
   - ❌ Learning cycle integration (NOT IMPLEMENTED)

5. **Backtesting**
   - ⚠️ Basic backtest() method exists in strategies
   - ⏳ Full backtesting framework (planned)
   - ⏳ Paper trading mode (planned)

6. **Additional Features**
   - ⏳ Trade journal / performance tracking
   - ⏳ Circuit breakers / kill switch
   - ⏳ Live order execution engine
   - ⏳ Position state management

---

## 9. Summary

### ✅ Strengths

1. **Domain-Specific** - Trading-specific logic and workflows
2. **Risk Management** - Strict risk controls (2%/6% rules)
3. **Strategy Framework** - Extensible strategy system
4. **Core Integration** - Uses meridian-core framework
5. **Larry Williams Strategies** - Proven trading approaches

### ⚠️ Gaps

1. **Self-Learning** - TradingLearningEngine not implemented
2. **Market Data** - MarketDataProvider incomplete
3. **Broker Integration** - IGConnector blocked, structure ready
4. **Backtesting** - Basic framework exists, needs enhancement
5. **Order Execution** - Live execution engine pending

### 🎯 Key Principles

1. **Extends Core** - Builds on meridian-core framework
2. **Risk-First** - Strict risk management always enforced
3. **Strategy-Driven** - Extensible strategy system
4. **Self-Learning** - Will learn from trading performance (planned)
5. **Data-Driven** - All decisions based on market data

### 📋 Next Steps

1. **Complete Trading Engine** - Finish TradingEngine and TradingSystem
2. **Implement Self-Learning** - Create TradingLearningEngine
3. **Complete Market Data** - Finish MarketDataProvider
4. **Broker Integration** - Resolve IGConnector blocking issue
5. **Enhance Backtesting** - Build full backtesting framework

---

**Last Updated:** 2025-11-20  
**Status:** ⚠️ In Development (Core Complete, Self-Learning Pending)  
**Version:** Current State

