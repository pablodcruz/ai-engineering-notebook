# Debugging Playbook

## Principles

- Isolate variables quickly.
- Inspect raw inputs and outputs.
- Keep a known-good baseline.
- Separate environment bugs from model behavior.
- Capture fixes while they are fresh.

## Triage Questions

- Did it work earlier?
- What changed?
- What is the exact error?
- Is this an environment issue, code issue, credential issue, network issue, service issue, or model-output issue?
- Can the problem be reproduced with a minimal request?

## Fast Checks

- Runtime version.
- Active environment.
- Installed dependencies.
- Credential presence.
- Endpoint or region.
- Network access.
- Quota or rate limits.
- Raw API response.

## Recovery Moves

| Situation | Move |
| --- | --- |
| One script fails | Run the smallest known-good request. |
| Many calls fail | Check credentials, quota, endpoint, and service status. |
| Output format is wrong | Inspect raw output, tighten schema, and add validation. |
| Retrieval is weak | Inspect chunks, metadata, query, and top matches. |
| Agent loops | Stop execution, inspect state, add loop limits and clearer exit rules. |

## Diagnose By Layer

Work from the outside in so a model prompt is not blamed for an infrastructure failure.

### 1. User Interface

- Confirm the action actually fired and was not blocked by browser validation.
- Inspect the HTTP status, response body, timeout, and displayed request id.
- Verify that recorded, cached, and live modes are labeled correctly.

### 2. Application Contract

- Validate required input fields and size limits.
- Confirm authentication and authorization checks ran before expensive work.
- Check schema parsing separately from response quality.

### 3. Runtime And Configuration

- Confirm the deployed revision and active environment.
- Check only whether required variables are present; never print their values.
- Verify package, runtime, endpoint, region, and model configuration.

### 4. External Service

- Correlate application and provider request ids.
- For an API authentication error, check for a missing or wrong key and confirm the credential source used by the running process.
- Separate permission, quota, rate-limit, timeout, and provider errors from authentication failures.
- Retry only failures known to be transient, with bounded backoff.

### 5. Model-Dependent Behavior

- Reproduce with a fixed, privacy-safe input.
- Inspect the exact prompt and model version used by the application.
- Compare the failure with the existing evaluation set before changing instructions.

### 6. Retrieval Or Tools

- Inspect selected sources or tool calls before inspecting prose quality.
- Verify permissions, arguments, results, and stopping conditions.
- Test “no result,” partial result, and prohibited-action paths deliberately.

## Incident Note Template

Capture enough information for another person to understand the failure without copying sensitive data:

```text
User-visible symptom:
First observed:
Affected deployment and revision:
Application request id:
Failure stage:
Provider status/code, if any:
Known-good comparison:
Root cause:
Fix or mitigation:
Regression check added:
Follow-up owner:
```

## Stop Conditions

Pause investigation and escalate when:

- Continuing would expose credentials, personal data, or customer content.
- A fix requires broader permissions or production mutation outside the task scope.
- Provider billing, legal, privacy, or retention policy must be decided by an owner.
- Repeated retries could increase cost or duplicate an external action.

## Practical Example

The deployed triage workflow once returned a generic `502`. The application request id led to a safe structured log showing provider status `429` and `insufficient_quota`. Adding provider credits resolved the request without changing application code. The lesson was diagnostic separation: the UI, gateway, Redis guard, and schema were healthy; the provider account lacked quota.
