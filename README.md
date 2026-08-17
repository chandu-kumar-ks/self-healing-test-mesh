# Self-Healing Test Mesh

A small, beginner-friendly proof of concept that demonstrates **AI-assisted
self-healing UI test automation** using Python and Playwright.

## Project Overview

Self-Healing Test Mesh is a Playwright + Pytest framework where a UI test
that starts with a **broken locator** does not simply fail. Instead, the
framework:

1. Detects the failure.
2. Captures the error and a snippet of the page's DOM.
3. Sends that context to an LLM and asks it to suggest replacement locators.
4. Validates each suggestion against the live page with Playwright (nothing
   from the AI is trusted blindly).
5. Retries the original action with the first valid, working locator.
6. Reports whether the test passed, failed, or was healed.

It is a portfolio-sized prototype, not a production framework - the goal is
to clearly demonstrate the self-healing *concept* end to end.

## Problem

UI automation is brittle. Every time a developer renames an id, restructures
a `<div>`, or tweaks a class name, previously passing Playwright/Selenium
tests break - even though the feature itself still works fine. Teams spend a
lot of time just re-pointing locators instead of finding real bugs.

## Solution

Instead of hardcoding a single locator and hoping it never changes, this
framework treats a locator failure as a recoverable event: it asks an LLM,
which has seen the current DOM, to suggest a small set of alternative
locators (preferring stable ones like `data-testid`, roles, and labels). Each
suggestion is validated with real Playwright calls before it's ever used, so
the AI can only *suggest* - it can never execute code or silently corrupt the
test.

## Architecture

```text
 Playwright Test
        │
        ▼
  Locator fails
        │
        ▼
 Capture failure + DOM  ───────────────┐
        │                              │
        ▼                              │
   Ask the LLM                         │   healing/ai_locator.py
        │                              │
        ▼                              │
 Parse JSON suggestions ◄──────────────┘
        │
        ▼
 Validate each suggestion  ───► healing/locator_validator.py
        │
        ▼
   Retry the action
        │
        ▼
   PASS / FAIL   ───────────────► reports/healing_report.html
```

## Technology Stack

- Python 3
- Playwright (sync API)
- Pytest
- An OpenAI-compatible LLM API (called with `requests`)
- `python-dotenv` for environment variables
- A small custom HTML report generator (no external reporting service)

## Project Structure

```text
self-healing-test-mesh/
│
├── tests/
│   └── test_login.py          # Demo test with an intentionally broken locator
│
├── pages/
│   └── login_page.py          # Page Object for the demo login page
│
├── healing/
│   ├── healer.py               # Orchestrates the self-healing flow
│   ├── ai_locator.py           # Talks to the LLM, parses JSON suggestions
│   └── locator_validator.py    # Validates suggestions against the live page
│
├── demo/
│   └── login.html              # Local demo page (no external site needed)
│
├── utils/
│   ├── config.py                # Reads settings from environment variables
│   └── report_generator.py      # Builds reports/healing_report.html
│
├── reports/                     # Generated HTML/JSON reports (git-ignored)
├── screenshots/                 # Screenshots captured on final failures
│
├── conftest.py                  # Playwright fixtures + report hook
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
└── README.md
```

## Installation

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

pip install -r requirements.txt

playwright install chromium
```

## Configuration

Copy the example env file and fill in your own LLM API key:

```bash
cp .env.example .env
```

Then edit `.env`:

```env
LLM_API_KEY=sk-...your key...
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
MAX_HEALING_ATTEMPTS=3
HEADLESS=true
```

If `LLM_API_KEY` is left empty, the framework will skip AI healing and the
demo test will simply fail with the original locator error - it will not
crash.

## Running Tests

From the project root:

```bash
pytest
```

To watch it run in a visible browser instead of headless:

```bash
HEADLESS=false pytest
```

After the run, open the generated report:

```text
reports/healing_report.html
```

## Expected Result

The demo test uses the locator `#login-btn`, but the real button in
`demo/login.html` has `id="login-button"`. On a normal run with a valid API
key, you should see something like:

```text
Test: test_login_with_self_healing

Original Status:   FAILED
Healing Attempted: YES
Original Locator:  #login-btn
Healed Locator:    #login-button
Confidence:        95%
Healing Result:    SUCCESS
Final Status:      PASSED (HEALED)
```

And the pytest run itself ends with `1 passed`, because the healed click
let the test complete successfully.

## Limitations

- This is a prototype: only `click()` actions are self-healed (via
  `Healer.smart_click`), not every possible Playwright action.
- Only one demo page and one broken locator are included.
- There is no persistent healing history across runs - each run's report is
  regenerated from scratch.
- The AI's suggestions are only as good as the DOM snippet and prompt given
  to it; very large or highly dynamic pages may need a smarter DOM capture
  strategy than "first N characters of `page.content()`".
- No CI/CD pipeline is included.

## Future Improvements

- Persist healing history across runs to spot flaky/renamed elements over time.
- Smarter locator scoring (e.g. weighting past healing success rates).
- Extend self-healing to `fill()`, `select_option()`, and other actions.
- Add API-level testing alongside UI testing.
- Add a GitHub Actions workflow to run the suite on every push.
- Test against more complex, multi-page applications.

## Troubleshooting

**`playwright._impl._api_types.Error: Executable doesn't exist`**
Run `playwright install chromium` again - the browser binary is separate
from the `playwright` pip package.

**Test fails with `Self-healing could not fix locator...` even with a valid API key**
Check that `LLM_API_KEY` is set correctly in `.env` and that your account has
access to the model set in `LLM_MODEL`. Also check the console output for
`[AILocatorEngine]` log lines - they explain exactly why healing didn't happen
(missing key, network error, bad JSON, etc.).

**`ModuleNotFoundError: No module named 'healing'` (or `pages`, `utils`)**
Make sure you're running `pytest` from the project root (`self-healing-test-mesh/`),
not from inside `tests/`. `conftest.py` adds the project root to `sys.path`
automatically when pytest picks it up from the root.

**Nothing happens / test just fails immediately without trying to heal**
This is expected if `LLM_API_KEY` is empty - the framework intentionally
skips calling the AI rather than failing with a confusing error.
