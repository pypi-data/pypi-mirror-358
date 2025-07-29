use pyo3::prelude::*;
use numpy::PyReadonlyArray1;
use rustalib_core::{macd::{MACD, MACDOutput}, Indicator};

#[pyclass(name = "MACD")]
pub struct PyMACD {
    inner: MACD,
}

#[pymethods]
impl PyMACD {
    #[new]
    fn new(fast_period: usize, slow_period: usize, signal_period: usize) -> Self {
        Self {
            inner: MACD::new(fast_period, slow_period, signal_period),
        }
    }

    /// Process next price incrementally, returns updated MACDOutput or None if insufficient data.
    fn next(&mut self, py: Python<'_>, value: f64) -> PyObject {
        match self.inner.next(value) {
            Some(out) => Py::new(py, PyMACDOutput::from(out)).unwrap().into(),
            None => py.None(),
        }
    }

    /// Calculate MACD over entire historical data, returns a list of MACDOutput or None.
    fn calculate_all(&mut self, py: Python<'_>, data: PyReadonlyArray1<'_, f64>) -> PyResult<Vec<PyObject>> {
        let vec = data
            .as_slice()
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid array: {}", e)))?;

        let results = self.inner.calculate_all(vec);

        let py_results = results.into_iter()
            .map(|opt| match opt {
                Some(out) => Py::new(py, PyMACDOutput::from(out)).unwrap().into(),
                None => py.None(),
            })
            .collect();

        Ok(py_results)
    }
}

/// Python representation of MACD output (macd, signal, histogram)
#[pyclass]
#[derive(Clone)]
pub struct PyMACDOutput {
    #[pyo3(get)]
    pub macd: f64,
    #[pyo3(get)]
    pub signal: f64,
    #[pyo3(get)]
    pub histogram: f64,
}

impl From<MACDOutput> for PyMACDOutput {
    fn from(o: MACDOutput) -> Self {
        Self {
            macd: o.macd,
            signal: o.signal,
            histogram: o.histogram,
        }
    }
}
