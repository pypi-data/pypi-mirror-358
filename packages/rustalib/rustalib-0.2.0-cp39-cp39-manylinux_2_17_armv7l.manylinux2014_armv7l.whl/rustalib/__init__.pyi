import numpy
from typing import Optional, List

class SMA:
    """Simple Moving Average indicator."""

    def __init__(self, period: int) -> None:
        """Initialize SMA with given period."""
        ...
    
    def calculate_all(self, data: numpy.ndarray) -> numpy.ndarray:
        """Calculate SMA over full input array, returns NaN for incomplete values."""
        ...
    
    def next(self, value: float) -> Optional[float]:
        """Add a new value and return updated SMA or None if not enough data."""
        ...

# EMA
class EMA:
    """
    Exponential Moving Average (EMA) indicator.
    Computes the EMA using an incremental smoothing method.
    """

    def __init__(self, period: int) -> None:
        """Initialize EMA with given period."""
        ...
    
    def next(self, value: float) -> Optional[float]:
        """Add a new value and return updated EMA or None if not enough data."""
        ...
    
    def calculate_all(self, data: numpy.ndarray) -> numpy.ndarray:
        """Calculate EMA over full input array, returns NaN for incomplete values."""
        ...

# MACD Output
class MACDOutput:
    """Represents a single output of the MACD indicator."""

    macd: float
    signal: float
    histogram: float

    def __init__(self, macd: float, signal: float, histogram: float) -> None:
        """Initialize a MACDOutput instance with macd, signal, and histogram values."""
        ...

# MACD
class MACD:
    """MACD (Moving Average Convergence Divergence) technical indicator."""

    def __init__(self, fast_period: int, slow_period: int, signal_period: int) -> None:
        """Initialize the MACD indicator with fast, slow, and signal periods."""
        ...

    def next(self, value: float) -> Optional[MACDOutput]:
        """Process the next price value and return the updated MACD output if available."""
        ...

    def calculate_all(self, data: numpy.ndarray) -> List[Optional[MACDOutput]]:
        """Calculate MACD for the entire input array and return a list of outputs (with None for warmup)."""
        ...
