use pyo3::{create_exception, pymodule};

mod exchange_rates;

#[pymodule]
mod pyfend {
	use nanorand::Rng as _;
	use pyo3::{
		prelude::{PyResult, pyfunction},
		pyclass, pymethods,
	};
	use std::sync::{LazyLock, Mutex};

	use crate::exchange_rates::ExchangeRateHandler;

	static WYRAND: LazyLock<Mutex<nanorand::WyRand>> = LazyLock::new(|| Mutex::new(nanorand::WyRand::new()));

	#[pyfunction]
	fn evaluate(input: &str, context: &mut Context) -> PyResult<String> {
		let Context(fend_context) = context;
		fend_context.set_random_u32_fn(|| WYRAND.lock().unwrap().generate::<u32>());
		fend_context.set_exchange_rate_handler_v1(ExchangeRateHandler {});
		match fend_core::evaluate(input, fend_context) {
			Ok(output) => Ok(output.get_main_result().to_string()),
			Err(err_msg) => Err(FendError::new_err(err_msg)),
		}
	}

	#[pyclass]
	struct Context(fend_core::Context);
	#[pymethods]
	impl Context {
		#[new]
		fn new() -> Self {
			Context(fend_core::Context::new())
		}

		/// Switch from SimpleText to TerminalFixedWidth mode
		fn set_output_mode_terminal(&mut self) {
			self.0.set_output_mode_terminal();
		}
	}

	#[pymodule_export]
	use super::FendError;
}

create_exception!(
	pyfend,
	FendError,
	pyo3::exceptions::PyException,
	"fend evaluation error"
);
