# AI System Review Checklist

Use this checklist when reviewing a prototype, planning a deployment, or preparing a customer workshop. Not every item must be implemented immediately, but every item should have an explicit answer.

## 1. Workflow Fit

- What user decision or task does the system improve?
- Why is model behavior needed instead of deterministic software alone?
- Is the architecture a prompted task, retrieval workflow, tool-using workflow, or human-review workflow?
- What is intentionally outside scope?

## 2. Inputs And Data

- Which inputs are accepted, and where are size and type limits enforced?
- Can inputs contain personal, confidential, regulated, or customer-owned data?
- Which data is sent to external providers?
- What is stored by the application, browser, logs, and provider?
- How are deletion, retention, freshness, and access permissions handled?

## 3. Model Contract

- Which model and prompt version run?
- What output schema or behavioral rubric defines success?
- Which requirements are validated deterministically?
- How does the system handle missing information, uncertainty, and refusal?
- Is there a rollback path for prompt, model, or schema changes?

## 4. Retrieval And Tools

- Are sources trusted, current, permission-aware, and traceable?
- Can the user inspect citations or evidence?
- Which tools are read-only, mutating, or prohibited?
- Which actions require approval?
- What loop, timeout, and stopping limits are enforced?

## 5. Human Oversight

- Who owns the final decision?
- Can a reviewer accept, correct, reject, or escalate?
- Are model suggestions visually distinct from approved outcomes?
- Are override reasons captured in a privacy-safe way?
- How do reviewed failures become evaluation cases?

## 6. Evaluation

- Does the evaluation set represent normal, boundary, missing-data, refusal, and adversarial cases?
- Are deterministic checks separated from subjective grading?
- Are aggregate results linked to case-level evidence?
- What threshold blocks a release?
- Who reviews quality when domain judgment is required?

## 7. Security And Abuse

- Where are credentials stored and rotated?
- Are authentication and authorization checked before expensive or sensitive work?
- Are rate limits and aggregate spend limits enforced server-side?
- Can untrusted content alter instructions, tool arguments, or data access?
- What is the emergency disable path?

## 8. Reliability And Observability

- Can application and provider requests be correlated safely?
- Are latency, usage, validation, refusal, and error stages observable?
- Do logs avoid prompts, credentials, personal data, and raw exception leakage?
- What happens during timeouts, provider outages, quota exhaustion, and bad deployments?
- Is there a recorded or degraded path that is labeled honestly?

## 9. Cost And Operations

- What drives cost per request and per completed workflow?
- Who owns provider budgets, quotas, and billing alerts?
- Which calls can be cached, recorded, batched, shortened, or avoided?
- Are public demos protected from unbounded use?
- What maintenance work is required after launch?

## 10. Enablement And Change Management

- Can the workflow be explained to technical and non-technical audiences?
- Are setup, failure recovery, and ownership documented?
- What customer taxonomy, policy, or process must be configured?
- Which metrics determine whether the rollout should expand?
- What feedback channel exists for users and reviewers?

## Review Outcome

Record the decision rather than ending with an unprioritized list:

```text
Current stage: prototype / controlled pilot / production
Approved use:
Prohibited use:
Top three risks:
Required controls before next stage:
Owner and review date:
Evidence links:
```
