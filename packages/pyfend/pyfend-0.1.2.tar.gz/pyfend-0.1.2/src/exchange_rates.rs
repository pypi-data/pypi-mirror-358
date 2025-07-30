// largely stolen from https://github.com/printfn/fend/blob/c504fbe6b2de0e02188f5ab6dd612f1856c9708d/cli/src/exchange_rates.rs

use std::{
	error, fmt,
	sync::Mutex,
	time::{Duration, Instant},
};

type Error = Box<dyn error::Error + Send + Sync + 'static>;
static RATES: Mutex<Option<ExchangeRateCache>> = Mutex::new(None);
struct ExchangeRateCache {
	rates: Vec<(String, f64)>,
	fetched_at: Instant,
}

const MAX_AGE: Duration = Duration::from_secs(60 * 60 * 24); // 24 hours

pub struct ExchangeRateHandler {}
impl fend_core::ExchangeRateFn for ExchangeRateHandler {
	fn relative_to_base_currency(&self, currency: &str) -> Result<f64, Error> {
		let mut lock = RATES.lock().unwrap();
		let option = lock.as_mut();
		let rates = match option {
			Some(rate_cache) => {
				if Instant::now().duration_since(rate_cache.fetched_at) > MAX_AGE {
					*lock = Some(get_exchange_rates()?);
					&lock.as_ref().unwrap().rates
				} else {
					&rate_cache.rates
				}
			},
			None => {
				*lock = Some(get_exchange_rates()?);
				&lock.as_ref().unwrap().rates
			},
		};
		for (c, rate) in rates {
			if currency == c {
				return Ok(*rate);
			}
		}
		Err(UnknownExchangeRate(currency.to_string()).into())
	}
}

fn get_exchange_rates() -> Result<ExchangeRateCache, Error> {
	let ts = Instant::now();
	let xml = http_get("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml")?;
	let rates = parse_exchange_rates(&xml)?;
	Ok(ExchangeRateCache { rates, fetched_at: ts })
}

fn parse_exchange_rates(exchange_rates: &str) -> Result<Vec<(String, f64)>, Error> {
	let err = "failed to load exchange rates";
	let mut result = vec![("EUR".to_string(), 1.0)];
	for l in exchange_rates.lines() {
		let l = l.trim();
		if !l.starts_with("<Cube currency=") {
			continue;
		}
		let l = l.strip_prefix("<Cube currency='").ok_or(err)?;
		let (currency, l) = l.split_at(3);
		let l = l.trim_start_matches("' rate='");
		let exchange_rate_eur = l.split_at(l.find('\'').ok_or(err)?).0;
		let exchange_rate_eur = exchange_rate_eur.parse::<f64>()?;
		if !exchange_rate_eur.is_normal() {
			return Err(err.into());
		}
		result.push((currency.to_string(), exchange_rate_eur));
	}
	if result.len() < 10 {
		return Err(err.into());
	}
	Ok(result)
}

fn http_get(url: &str) -> Result<String, Error> {
	let response = minreq::get(url).send()?;
	Ok(response.as_str()?.to_string())
}

#[derive(Debug, Clone)]
struct UnknownExchangeRate(String);
impl error::Error for UnknownExchangeRate {}

impl fmt::Display for UnknownExchangeRate {
	fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
		write!(f, "currency exchange rate for {} is unknown", self.0)
	}
}
