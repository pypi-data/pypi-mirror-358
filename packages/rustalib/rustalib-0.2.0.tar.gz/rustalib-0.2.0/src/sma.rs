use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use rustalib_core::{sma::SMA, Indicator};
use numpy::{PyArray1, PyReadonlyArray1};

#[pyclass(name = "SMA")]
pub struct PySMA {
    inner: SMA,
}

#[pymethods]
impl PySMA {
    #[new]
    fn new(period: usize) -> Self {
        Self {
            inner: SMA::new(period),
        }
    }

    /// Calculate SMA over full input array (returns NaN for initial incomplete values).
    fn calculate_all<'py>(
        &mut self,
        py: Python<'py>,
        data: PyReadonlyArray1<'_, f64>,
    ) -> PyResult<Py<PyArray1<f64>>> {
        let vec = data
            .as_slice()
            .map_err(|e| PyValueError::new_err(format!("Invalid array: {}", e)))?;

        let result = self.inner.calculate_all(vec);
        let nan_result: Vec<f64> = result.into_iter().map(|v| v.unwrap_or(f64::NAN)).collect();

        let py_array = PyArray1::from_vec(py, nan_result);
        Ok(py_array.to_owned().into())
    }

    /// Push one new value into the SMA (rolling), and return updated result.
    fn next(&mut self, value: f64) -> Option<f64> {
        self.inner.next(value)
    }
}
