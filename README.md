# Self-Healing Test Mesh

**AI-assisted Playwright test automation that detects broken locators, asks an LLM for alternatives, validates them against the live page, and retries the failed action automatically.**

> Portfolio-focused proof of concept demonstrating how AI can reduce locator maintenance in UI test automation.

## Why this project?

UI automation can become brittle when developers rename element IDs, change classes, or restructure the DOM. A test may fail even though the application behavior is still correct.

This project treats a broken locator as a **recoverable test event** instead of an immediate test failure.

## How self-healing works

```text
┌──────────────────────┐
│ Playwright + Pytest  │
└──────────┬───────────┘
           │
           ▼
   Locator/action fails
           │
           ▼
┌──────────────────────┐
│ Capture error + DOM  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ AI Locator Engine    │
│ LLM suggests         │
│ replacement locators │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Locator Validator    │
│ Playwright validates │
│ each suggestion      │
└──────────┬───────────┘
           │
           ▼
     Retry action
       /      \
      ▼        ▼
   PASS      FAIL
   HEALED
           │
           ▼
   Healing report
```

### Key design principle

**The LLM only suggests locators. Playwright decides whether a locator actually works.**

The framework does not blindly trust an AI response. Every suggested locator is validated against the current page before it is used.

## Demo scenario

The included login page intentionally contains a changed button ID:

```text
Test expects:  #login-btn
Actual page:   #login-button
```

The test initially fails to find `#login-btn`. The healing flow sends the failure context and DOM information to the LLM, receives `#login-button` as a suggestion, validates it with Playwright, retries the click, and allows the test to pass.

Example result:

```text
Original Status:   FAILED
Original Locator:  #login-btn
Healed Locator:    #login-button
Confidence:        95%
Healing Result:    SUCCESS
Final Status:      PASSED (HEALED)
```

## Architecture

| Component | Responsibility |
|---|---|
| `tests/` | Pytest test cases and self-healing scenarios |
| `pages/` | Page Object Model implementation |
| `healing/healer.py` | Coordinates failure detection, healing, validation and retry |
| `healing/ai_locator.py` | Sends failure context to an OpenAI-compatible LLM endpoint and parses suggestions |
| `healing/locator_validator.py` | Validates AI-generated locators against the live Playwright page |
| `utils/config.py` | Loads environment-based configuration |
| `utils/report_generator.py` | Generates the HTML healing report |
| `mock_llm_server.py` | Local deterministic LLM-compatible server for demos without an API key |

## Technology Stack

- **Python 3.13**
- **Playwright 1.61**
- **Pytest 8.3**
- **Requests**
- **python-dotenv**
- **OpenAI-compatible chat completion API**
- **Custom HTML healing report**
- **Git / GitHub**

## Project Structure

```text
self-healing-test-mesh/
│
├── demo/
│   └── login.html                 # Local demo application
│
├── healing/
│   ├── __init__.py
│   ├── ai_locator.py              # LLM integration + JSON parsing
│   ├── healer.py                  # Self-healing orchestration
│   └── locator_validator.py       # Locator validation
│
├── pages/
│   ├── __init__.py
│   └── login_page.py              # Page Object Model
│
├── tests/
│   └── test_login.py              # Broken-locator healing test
│
├── utils/
│   ├── __init__.py
│   ├── config.py                  # Environment configuration
│   └── report_generator.py        # HTML report generation
│
├── reports/                       # Generated reports (ignored except .gitkeep)
├── screenshots/                   # Failure screenshots (ignored except .gitkeep)
├── mock_llm_server.py             # Local mock LLM endpoint
├── conftest.py                    # Pytest / Playwright fixtures and hooks
├── pytest.ini
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/chandu-kumar-ks/self-healing-test-mesh.git
cd self-healing-test-mesh
```

### 2. Create a virtual environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Configure the local mock LLM

This project can be run **without an API key** using the included deterministic mock LLM server.

Copy the example configuration:

```bash
copy .env.example .env
```

For macOS/Linux:

```bash
cp .env.example .env
```

The example configuration already points to the local mock server:

```env
LLM_API_KEY=mock-key
LLM_API_BASE=http://127.0.0.1:8000/v1
LLM_MODEL=mock-gpt-4o-mini
MAX_HEALING_ATTEMPTS=3
HEADLESS=true
```

The mock server does not contact an external AI service. It returns a deterministic locator suggestion so the complete self-healing flow can be demonstrated locally and repeatably.

## Run the self-healing test

Open **Terminal 1** and start the mock LLM server:

```bash
python mock_llm_server.py
```

You should see:

```text
Mock LLM Server
http://127.0.0.1:8000
Endpoint: /v1/chat/completions
```

Keep that terminal running.

Open **Terminal 2**, activate the virtual environment, and run:

```bash
pytest -v -s
```

Expected result:

```text
collected 1 item

tests/test_login.py::test_login_with_self_healing PASSED

1 passed
```

The mock server should also show successful requests such as:

```text
[MockLLM] "POST /v1/chat/completions HTTP/1.1" 200 -
```

### Run with a visible browser

Change `.env` to:

```env
HEADLESS=false
```

Then run:

```bash
pytest -v -s
```

## Healing report

After the test run, the framework generates a report under:

```text
reports/healing_report.html
```

The report records the original locator, healing attempt, replacement locator, and final result.

## Optional: use a real LLM

The project uses an **OpenAI-compatible API contract**, so the same integration can be pointed to a real provider later.

Update `.env` with the provider's API key, base URL, and model:

```env
LLM_API_KEY=your_real_api_key
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=your_model_name
```

For portfolio demonstrations, the included mock LLM is sufficient and avoids exposing credentials or requiring paid API access.

## Safety and validation

The self-healing flow includes several safeguards:

- The LLM receives a constrained locator-generation prompt.
- The LLM does not execute Python, JavaScript, or shell commands.
- AI output is parsed as structured JSON.
- Suggested locators are validated against the live page.
- Only validated locators are used for the retry.
- Healing attempts are capped by `MAX_HEALING_ATTEMPTS`.
- API keys are loaded from `.env` and excluded from Git with `.gitignore`.

## Current scope

This is a focused proof of concept rather than a production-grade autonomous testing platform.

Currently it demonstrates:

- Playwright UI automation
- Page Object Model
- Pytest execution
- Broken locator detection
- LLM-assisted locator suggestion
- Live locator validation
- Automatic retry after healing
- HTML healing reports
- Deterministic local mock LLM execution

## Limitations

- The current demo focuses on healing `click()` actions.
- The repository contains one small demo application and one primary healing scenario.
- Healing history is not persisted between runs.
- The mock LLM is deterministic and does not perform real reasoning.
- Large or highly dynamic pages would require more advanced DOM extraction and locator-ranking strategies.
- CI/CD automation is not yet included.

## Roadmap

- [ ] Add healing support for `fill()` and other Playwright actions
- [ ] Add persistent healing history and locator success scoring
- [ ] Add multiple broken-locator scenarios
- [ ] Add API testing examples
- [ ] Add GitHub Actions CI/CD
- [ ] Add richer test/healing analytics
- [ ] Add optional real-LLM integration examples

## Why this is useful for QA automation

The project demonstrates a practical approach to reducing test-maintenance effort: instead of replacing every broken locator manually, the framework can use AI to propose alternatives while keeping deterministic browser validation in control.

It combines **Playwright + Pytest + Page Object Model + API integration + AI-assisted locator healing + reporting**, making it a practical demonstration of modern QA automation engineering.
