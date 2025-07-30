all: release

clean:
	cargo clean

release: clean
	cargo build --release

python: clean
	maturin build --release

pypi: clean
	maturin build --release --sdist
