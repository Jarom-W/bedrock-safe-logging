.PHONY: test test-integration build scan install activate

test:
	pytest -m "not integration" -q

test-integration:
	pytest -m "integration" -q --log-cli-level=INFO -s

build:
	docker compose up --build

scan:
	python3 ./scripts/secret_scan.py

install:
	pip3 install -r requirements.txt

activate:
	source venv/bin/activate
