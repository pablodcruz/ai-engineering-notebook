# Browser Testing

The Support Triage Review Console has an isolated Playwright suite that runs against recorded evidence only. It does not use a personal browser profile, OpenAI key, Redis, demo access code, or Gmail session.

## Local Setup

Install Node.js, then run from the repository root:

```powershell
npm ci
npx playwright install chromium
npm run test:browser
```

Playwright downloads a matching Chromium build into its own machine-level cache. The tests start a temporary Python static server at `127.0.0.1:4173`, open fresh isolated browser contexts, and stop the server when the run completes.

Use a visible browser for local debugging:

```powershell
npm run test:browser:headed
```

## Covered Workflows

- Load and validate a recorded recommendation without calling `/api/triage`.
- Populate the human-review form from the model suggestion.
- Accept a recommendation and update queue and agreement metrics.
- Require an override reason before saving an edited decision.
- Preserve model and final human decisions separately.
- Download the versioned synthetic review export.
- Verify exports exclude access codes and ticket text.
- Reset browser-local review history.
- Validate the browser-based demo-access request URL without opening Gmail or sending mail.

## CI Behavior

GitHub Actions installs Node dependencies from `package-lock.json`, installs isolated Chromium with its Linux dependencies, runs the suite headlessly, and uploads the Playwright HTML report plus failure traces, screenshots, and videos when present.

Every Playwright test receives a fresh browser context. This makes the suite reproducible on another developer machine and prevents access to history, passwords, extensions, cookies, or sessions from Chrome or Brave.

## Deliberate Boundaries

The suite does not:

- Exercise the billable live-provider path.
- Store or submit a demo access code.
- Sign into Gmail or send an access-request email.
- Test Vercel, Redis, or OpenAI availability.
- Replace Python gateway tests or AI behavioral evals.

The separate health and live smoke checks cover deployed API boundaries. Browser tests protect the deterministic user workflow without introducing provider cost or personal credentials.
