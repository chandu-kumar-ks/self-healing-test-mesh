# AI-Powered Self-Healing Test Mesh

An AI-assisted test automation framework built with Python, Playwright, and Pytest that automatically detects failed UI locators, generates alternative locators, validates them, and retries the test using the healed locator.

This project demonstrates how self-healing techniques can reduce test maintenance when UI locators change.

## Key Features

- Playwright-based UI test automation
- Self-healing locator mechanism
- AI-assisted locator suggestions
- Mock LLM for local AI simulation
- Automatic retry with healed locators
- Locator validation before retry
- Configurable healing attempts
- Healing confidence score
- HTML and JSON test reports
- Failure and healed execution screenshots
- Pytest integration

## How It Works

The framework follows this flow:

Test Case
    ↓
Page Object
    ↓
Playwright
    ↓
Locator Validation
    ↓
Locator Failure
    ↓
AI Locator Engine
    ↓
Mock LLM
    ↓
Suggested Locator
    ↓
Locator Validation
    ↓
Retry with Healed Locator
    ↓
Test Result
    ↓
HTML / JSON Report

### Self-Healing Flow

1. The test starts with the original locator.
2. Playwright attempts to interact with the element.
3. If the locator fails, the healing mechanism is triggered.
4. The AI locator engine requests an alternative locator.
5. The Mock LLM returns a suggested locator.
6. The suggested locator is validated against the page.
7. If the locator is valid, the test retries using the healed locator.
8. The healing result and confidence score are recorded.
9. Execution evidence is captured through screenshots and reports.

## Self-Healing Example

The test initially uses:

#login-btn

The application contains the updated locator:

#login-button

The original locator fails:

Original Status: FAILED
Original Locator: #login-btn

The self-healing engine identifies the updated locator:

Healed Locator: #login-button
Confidence: 95%
Healing Result: SUCCESS

The test is then retried using the healed locator:

Final Status: PASSED (HEALED)

## Execution Result

Example test execution:

tests/test_login.py::test_login_with_self_healing PASSED

1 passed in 4.58s

## Healing Report

The framework generates a report containing the following information:

Test / Action: Login button
Original Status: FAILED
Healing Attempted: YES
Original Locator: #login-btn
Healed Locator: #login-button
Confidence: 95%
Healing Result: SUCCESS
Final Status: PASSED (HEALED)

## Execution Evidence

The framework captures screenshots during execution.

### Original Locator Failure

The failed execution screenshot is stored as:

screenshots/test_login_with_self_healing_failed.png

### Healed Execution

The successful healed execution screenshot is stored as:

screenshots/test_login_with_self_healing_healed.png

## Tech Stack

- Python
- Playwright
- Pytest
- Mock LLM
- HTML
- CSS
- JSON
- Git
- GitHub

## Project Structure
```
self-healing-test-mesh/
│
├── demo/
│   └── login.html
│
├── healing/
│   ├── __init__.py
│   ├── ai_locator.py
│   ├── healer.py
│   └── locator_validator.py
│
├── pages/
│   ├── __init__.py
│   └── login_page.py
│
├── reports/
│   └── .gitkeep
│
├── screenshots/
│   ├── .gitkeep
│   ├── test_login_with_self_healing_failed.png
│   └── test_login_with_self_healing_healed.png
│
├── tests/
│   └── test_login.py
│
├── utils/
│   ├── __init__.py
│   ├── config.py
│   └── report_generator.py
│
├── mock_llm_server.py
├── conftest.py
├── pytest.ini
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```
## Getting Started

### 1. Clone the Repository

git clone https://github.com/chandu-kumar-ks/self-healing-test-mesh.git

cd self-healing-test-mesh

### 2. Create a Virtual Environment

python -m venv .venv

### 3. Activate the Virtual Environment

Windows:

.venv\Scripts\activate

### 4. Install Dependencies

pip install -r requirements.txt

### 5. Install Playwright Browsers

playwright install

## Start the Mock LLM

This project uses a local Mock LLM instead of requiring a paid external API.

Open a separate terminal and run:

python mock_llm_server.py

The Mock LLM server runs at:

http://127.0.0.1:8000

Endpoint:

/v1/chat/completions

The Mock LLM allows the self-healing workflow to be demonstrated locally without requiring an external AI API.

## Run the Tests

With the Mock LLM running in a separate terminal, execute:

pytest -v -s

Example:

tests/test_login.py::test_login_with_self_healing PASSED

1 passed

## Generated Reports

After execution, the framework generates:

reports/healing_report.html
reports/healing_report.json

The reports contain:

- Original locator
- Original test status
- Healing attempt status
- Healed locator
- Confidence score
- Healing result
- Final test status
- Original error

## Screenshots

Execution screenshots are stored in:

screenshots/test_login_with_self_healing_failed.png
screenshots/test_login_with_self_healing_healed.png

These screenshots provide visual evidence of the failed original locator and the successful healed execution.

## Project Objective

Traditional UI automation tests can become unstable when application developers change element IDs, attributes, or other locator properties.

For example:

Before UI change:

#login-btn

After UI change:

#login-button

A traditional automation test may fail and require manual maintenance.

This project demonstrates an alternative approach where the framework detects the locator failure, requests an alternative locator, validates it, and retries the test automatically.

## Future Enhancements

- Integration with production LLM APIs
- Support for multiple locator strategies
- DOM-based similarity analysis
- Historical locator learning
- Healing success analytics
- CI/CD integration
- Multi-browser execution
- Automatic locator maintenance
- Enhanced AI confidence scoring

## What This Project Demonstrates

This project demonstrates practical experience with:

- Test automation framework design
- Playwright
- Pytest
- Page Object Model
- Locator validation
- Self-healing automation
- AI-assisted testing concepts
- Mock API integration
- Test reporting
- Screenshot-based execution evidence
- Git and GitHub

## Author

K S Chandu Kumar
