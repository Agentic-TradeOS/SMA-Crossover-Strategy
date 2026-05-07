export interface SMACrossoverConfig {
  fastPeriod: number;
  slowPeriod: number;
  stopLossPct: number;
  positionSizePct: number;
}

export const defaultConfig: SMACrossoverConfig = {
  fastPeriod: 10,
  slowPeriod: 30,
  stopLossPct: 0.08,
  positionSizePct: 0.20,
};

export function calculateSMA(closes: number[], period: number): number[] {
  return closes.map((_, i) => {
    if (i < period - 1) return NaN;
    return closes.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0) / period;
  });
}

export function generateSignals(
  closes: number[],
  config: SMACrossoverConfig = defaultConfig
): Array<{ index: number; signal: 1 | -1 | 0; smaFast: number; smaSlow: number }> {
  const fast = calculateSMA(closes, config.fastPeriod);
  const slow = calculateSMA(closes, config.slowPeriod);

  return closes.map((_, i) => {
    const smaFast = fast[i];
    const smaSlow = slow[i];
    if (isNaN(smaFast) || isNaN(smaSlow) || i === 0) {
      return { index: i, signal: 0 as const, smaFast, smaSlow };
    }
    const goldenCross = fast[i - 1] <= slow[i - 1] && smaFast > smaSlow;
    const deathCross = fast[i - 1] >= slow[i - 1] && smaFast < smaSlow;
    const signal = goldenCross ? 1 : deathCross ? -1 : 0;
    return { index: i, signal: signal as 1 | -1 | 0, smaFast, smaSlow };
  });
}

export function getCurrentSignal(
  closes: number[],
  config: SMACrossoverConfig = defaultConfig
): 1 | -1 | 0 {
  const signals = generateSignals(closes, config);
  return signals[signals.length - 1]?.signal ?? 0;
}

export default { defaultConfig, generateSignals, getCurrentSignal };
