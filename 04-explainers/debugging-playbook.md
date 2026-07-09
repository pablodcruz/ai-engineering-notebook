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
