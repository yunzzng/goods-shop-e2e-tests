# goods-shop-e2e-tests

Goods Shop 웹 애플리케이션의 E2E 테스트 자동화 프로젝트입니다.

## Tech Stack

- Python
- pytest
- Playwright

## Project Structure

```text
goods-shop-e2e-tests/
├── pages/          # Page Object
├── tests/          # Test cases
├── utils/          # Shared helpers
├── artifacts/      # Test reports and generated artifacts
├── conftest.py     # pytest fixtures and common setup
├── pytest.ini      # pytest configuration
└── requirements.txt
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install
```

## Run Tests

```bash
pytest
```

## Repository

```text
git@github.com:yunzzng/goods-shop-e2e-tests.git
```
