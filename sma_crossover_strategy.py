"""
SMA Crossover Strategy
A trend-following strategy using fast and slow Simple Moving Averages.

Entry: Buy when fast SMA crosses above slow SMA (Golden Cross)
Exit: Sell when fast SMA crosses below slow SMA (Death Cross)

Author: Agentic Trading ML
Version: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Signal:
    """Trading signal data class"""
    timestamp: datetime
    symbol: str
    action: str  # 'buy' or 'sell'
    price: float
    confidence: float = 1.0
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Trade:
    """Trade record data class"""
    entry_date: datetime
    exit_date: Optional[datetime]
    symbol: str
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    pnl: float = 0.0
    pnl_pct: float = 0.0
    duration_days: int = 0


class SMACrossoverStrategy:
    """
    SMA Crossover Strategy
    
    This strategy generates buy signals when the fast Simple Moving Average 
    crosses above the slow SMA, and sell signals when the fast SMA crosses below 
    the slow SMA.
    
    Default: Fast=10, Slow=30 (medium-term trend)
    """
    
    def __init__(
        self,
        fast_period: int = 10,
        slow_period: int = 30,
        stop_loss_pct: float = 0.08,
        position_size_pct: float = 0.20,
    ):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.stop_loss_pct = stop_loss_pct
        self.position_size_pct = position_size_pct
        
        if slow_period <= fast_period:
            raise ValueError("slow_period must be greater than fast_period")
    
    def calculate_sma(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return prices.rolling(window=period).mean()
    
    def generate_signals(
        self,
        data: pd.DataFrame,
        price_col: str = 'close',
    ) -> List[Signal]:
        """Generate trading signals from price data"""
        signals = []
        
        fast_sma = self.calculate_sma(data[price_col], self.fast_period)
        slow_sma = self.calculate_sma(data[price_col], self.slow_period)
        
        for i in range(1, len(data)):
            if pd.isna(fast_sma.iloc[i]) or pd.isna(slow_sma.iloc[i]):
                continue
                
            prev_fast = fast_sma.iloc[i-1]
            prev_slow = slow_sma.iloc[i-1]
            curr_fast = fast_sma.iloc[i]
            curr_slow = slow_sma.iloc[i]
            
            # Golden Cross: fast crosses above slow
            if prev_fast <= prev_slow and curr_fast > curr_slow:
                signals.append(Signal(
                    timestamp=data.index[i],
                    symbol=data.get('symbol', 'UNKNOWN').iloc[0] if hasattr(data.get('symbol', pd.Series()), 'UNKNOWN'),
                    action='buy',
                    price=data[price_col].iloc[i],
                ))
            # Death Cross: fast crosses below slow
            elif prev_fast >= prev_slow and curr_fast < curr_slow:
                signals.append(Signal(
                    timestamp=data.index[i],
                    symbol=data.get('symbol', 'UNKNOWN'),
                    action='sell',
                    price=data[price_col].iloc[i],
                ))
        
        return signals
    
    def run_backtest(
        self,
        data: pd.DataFrame,
        price_col: str = 'close',
        initial_capital: float = 100000.0,
    ) -> Dict[str, Any]:
        """Run backtest on historical data"""
        signals = self.generate_signals(data, price_col)
        
        cash = initial_capital
        position = 0
        trades = []
        entry_price = 0.0
        entry_date = None
        
        prices = data[price_col].values
        dates = data.index
        
        for i, sig in enumerate(signals):
            if sig.action == 'buy' and position == 0:
                position = (cash * self.position_size_pct) / sig.price
                cash -= position * sig.price
                entry_price = sig.price
                entry_date = sig.timestamp
            elif sig.action == 'sell' and position > 0:
                pnl = (sig.price - entry_price) * position
                pnl_pct = (sig.price - entry_price) / entry_price
                
                trades.append(Trade(
                    entry_date=entry_date,
                    exit_date=sig.timestamp,
                    symbol=sig.symbol,
                    entry_price=entry_price,
                    exit_price=sig.price,
                    quantity=position,
                    pnl=pnl,
                    pnl_pct=pnl_pct,
                    duration_days=(sig.timestamp - entry_date).days if entry_date else 0,
                ))
                
                cash += position * sig.price
                position = 0
        
        # Close any open position
        if position > 0:
            final_price = prices[-1]
            pnl = (final_price - entry_price) * position
            trades.append(Trade(
                entry_date=entry_date,
                exit_date=dates[-1],
                symbol='UNKNOWN',
                entry_price=entry_price,
                exit_price=final_price,
                quantity=position,
                pnl=pnl,
                pnl_pct=pnl / entry_price,
                duration_days=(dates[-1] - entry_date).days if entry_date else 0,
            ))
            cash += position * final_price
        
        total_return = (cash - initial_capital) / initial_capital
        winning_trades = [t for t in trades if t.pnl > 0]
        
        return {
            'total_return': total_return,
            'final_capital': cash,
            'num_trades': len(trades),
            'winning_trades': len(winning_trades),
            'win_rate': len(winning_trades) / len(trades) if trades else 0,
            'trades': trades,
        }


if __name__ == '__main__':
    # Example usage
    import yfinance as yf
    
    # Fetch sample data
    data = yf.download('AAPL', start='2020-01-01', end='2024-01-01')
    
    strategy = SMACrossoverStrategy(fast_period=10, slow_period=30)
    results = strategy.run_backtest(data)
    
    print(f"Total Return: {results['total_return']*100:.2f}%")
    print(f"Num Trades: {results['num_trades']}")
    print(f"Win Rate: {results['win_rate']*100:.2f}%")
