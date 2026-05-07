# SMA Crossover Strategy

A trend-following strategy based on the intersection of fast and slow Simple Moving Averages.

## How It Works

| Signal | Condition | Action |
|---|---|---|
| **Golden Cross** | Fast SMA crosses **above** Slow SMA | BUY — enter long |
| **Death Cross** | Fast SMA crosses **below** Slow SMA | SELL — exit long |
| **Stop Loss** | Price drops 8% from entry | EXIT — capital protection |

## Parameters

| Parameter | Default | Description |
|---|---|---|
| Fast MA | 10 | Short-term moving average period |
| Slow MA | 30 | Long-term moving average period |
| MA Type | SMA | Simple Moving Average |
| Stop Loss | 8% | Max loss per trade |

## When It Works Best

- **Trending markets** — medium-term trends
- **Liquid stocks** — AAPL, MSFT, GOOGL, SPY
- **Daily timeframe** — designed for position trading

## When to Avoid

- Choppy / sideways markets (generates false signals)
- Earnings weeks (gaps can blow through stop loss)
- Low liquidity assets

## Sample Backtest (AAPL, 2020–2024)

```
Total Return:     +45.2%
Annualized:     +10.2%
Sharpe Ratio:   1.15
Max Drawdown:  -12.3%
Win Rate:      58%
```

## Files

```
strategy-sma-crossover/
├── strategy.json          # Visual builder template
├── README.md           # This file
├── typescript/
│   └── sma-crossover-strategy.ts   # TypeScript implementation
├── python/
│   ├── sma_crossover_strategy.py  # Python implementation
│   └── requirements.txt       # Dependencies
└── examples/
    └── example-real-execution.ts   # Real-world example
```

## Usage

### TypeScript
```typescript
import { generateSignals, getCurrentSignal } from './typescript/sma-crossover-strategy';

const closes = [/* price data */];
const signal = getCurrentSignal(closes); // 1 = buy, -1 = sell, 0 = hold
```

### Python
```python
from sma_crossover_strategy import SMACrossoverStrategy

strategy = SMACrossoverStrategy(fast_period=10, slow_period=30)
results = strategy.run_backtest(data)
```

## Author

Agentic Trading ML
