import pandas as pd
import numpy as np
from rustalib import MACD

def main():
    
    # Load data from cvs
    df = pd.read_csv("examples/data/SPY_1D.csv")
    close = df["Close"].to_numpy(dtype=np.float64)
    
    # Create Moving Average Convergence Divergence (MACD) indicator
    fast_period = 12
    slow_period = 26
    signal_period = 9
    
    # Backtesting mode
    macd = MACD(fast_period, slow_period, signal_period)
    results = macd.calculate_all(close)

    # show last 10 values
    print("Last 10 MACD outputs:")
    for output in results[-10:]:
        if output is not None:
            print(f"MACD: {output.macd:.4f}, Signal: {output.signal:.4f}, Histogram: {output.histogram:.4f}")
        else:
            print("None")

if __name__ == "__main__":
    main()