import pandas as pd
import numpy as np

from rustalib import EMA

df = pd.read_csv("examples/data/SPY_1D.csv")
close = df["Close"].to_numpy(dtype=np.float64)

ema = EMA(20)
df["SMA20"] = ema.calculate_all(close)
print(df.tail())
