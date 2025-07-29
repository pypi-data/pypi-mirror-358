pub mod sma;
pub mod ema;
pub mod macd;

use pyo3::prelude::*;
use sma::PySMA;
use ema::PyEMA;
use macd::{PyMACD, PyMACDOutput};

#[pymodule]
pub fn rustalib(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PySMA>()?;
    m.add_class::<PyEMA>()?;
    m.add_class::<PyMACD>()?;
    m.add_class::<PyMACDOutput>()?;

    Ok(())
}