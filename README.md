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
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/playwright install
```

## Run Tests

```bash
./run_tests.sh -q
```

특정 파일만 실행하려면:

```bash
./run_tests.sh tests/test_login.py -q
```

테스트가 끝나면 `artifacts/dashboard.html`을 자동으로 엽니다.

브라우저나 실행 모드를 지정하려면:

```bash
PLAYWRIGHT_HEADLESS=false ./run_tests.sh -q
PLAYWRIGHT_BROWSER=webkit ./run_tests.sh -q
PLAYWRIGHT_BROWSER=firefox ./run_tests.sh -q
```

## Troubleshooting

Playwright 브라우저 실행이 안 되면 먼저 브라우저를 다시 설치합니다.

```bash
./.venv/bin/playwright install
```

macOS에서 Chromium 실행이 막히면 WebKit이나 Firefox로 먼저 확인합니다.

```bash
PLAYWRIGHT_BROWSER=webkit ./run_tests.sh -q
PLAYWRIGHT_BROWSER=firefox ./run_tests.sh -q
```

## Repository

```text
git@github.com:yunzzng/goods-shop-e2e-tests.git
```
