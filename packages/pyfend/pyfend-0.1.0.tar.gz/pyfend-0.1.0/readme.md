python bindings for [fend-core](https://crates.io/crates/fend-core)

## testing
do not run `uv -m unittest`. bypass the uv cache:
```
uv run maturin develop --uv && .venv/bin/python -m unittest
```
