import pandas as pd
import numpy as np

from rustalib import SMA

df = pd.read_csv("examples/data/SPY_1D.csv")
close = df["Close"].to_numpy(dtype=np.float64)

sma = SMA(20)
df["SMA20"] = sma.calculate_all(close)
print(df.tail())