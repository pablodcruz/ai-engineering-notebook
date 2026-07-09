# API And SDK Integration Lab

## Skill Level

Beginner to intermediate.

## Duration

30 to 60 minutes.

## Learning Objectives

- Make a first model API call.
- Understand credentials and environment variables.
- Modify a sample request.
- Handle common errors.
- Separate environment failures from model behavior.

## Prerequisites

- Python 3.10 or newer.
- An active virtual environment.
- Provider SDK installed for the model service you want to test.
- Credential environment variable configured, such as `OPENAI_API_KEY`.
- A known-good model name or endpoint from the provider documentation.

## Setup

1. Confirm the active interpreter:

   ```bash
   python --version
   ```

2. Confirm the active package environment:

   ```bash
   python -m pip --version
   ```

3. Confirm the credential exists without printing the secret value.
4. Create a minimal request script.
5. Keep the original request unchanged as the known-good baseline.

## Exercise

1. Confirm runtime and package installation.
2. Configure credentials through environment variables or local secret handling.
3. Run a minimal request.
4. Print or inspect the raw response.
5. Change the prompt or input payload.
6. Add basic error handling.
7. Record the exact error and fix for any failure.

## Expected Output

The lab should produce:

- A successful minimal API response.
- A note showing which environment variable was required.
- A changed prompt or payload and its response.
- One captured failure mode with the fix used.
- A known-good command or script that can be rerun later.

## Common Failure Modes

| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| Authentication error | Missing or wrong key | Check credential source and active shell. |
| Module not found | Dependency not installed in current environment | Confirm package manager and virtual environment. |
| Endpoint error | Wrong base URL or region | Verify endpoint and provider configuration. |
| Rate limit | Too many requests or quota limit | Slow down, retry later, or switch credentials. |
| Empty or odd response | Prompt or response parsing issue | Inspect raw response before parsing. |
| Works in one shell but not another | Environment variable set in only one session | Set credentials in the active terminal or project environment file. |

## Build Notes

Keep one known-good request ready. It gives the experiment a baseline before changing prompts, parameters, or parsing logic.

Do not commit secrets, response logs containing sensitive data, or local `.env` files.

## Debrief

- Was the first failure an environment issue, code issue, service issue, or prompt issue?
- Which command proved the environment was ready?
- What would you log in a production application?
- What should remain outside source control?
