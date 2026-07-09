# Cloud AI Fundamentals

## Why This Matters

Give enough cloud context to support AI labs, enterprise discussions, and troubleshooting.

## Concepts To Know

- Identity and access management.
- API keys, service accounts, roles, and permissions.
- Regions and data residency.
- Managed model APIs.
- Storage for documents and datasets.
- Compute for application hosting.
- Logging, monitoring, and cost controls.
- Network access and firewall constraints.

## AI App Deployment Pattern

Most simple AI applications need:

- Frontend or client.
- Backend service.
- Model API integration.
- Secret management.
- Data store or retrieval index.
- Observability.
- Authentication and authorization.

## Common Prototype Issues

- Missing credentials.
- Wrong region or endpoint.
- Expired keys.
- Permissions too narrow.
- Dependency or runtime mismatch.
- Corporate network blocks.
- Quota or rate limits.

## Engineering Lens

Cloud deployment turns a local AI demo into an operated system. The hard questions move from "can it answer?" to "who can access it, what does it cost, how does it fail, and how will we know?"

Design decisions to make explicit:

- Which service owns secret storage.
- Which identity the app uses to call model APIs.
- Where documents, embeddings, logs, and traces live.
- Which region and data residency constraints apply.
- How deployments roll back.

## What To Evaluate

- Credential and permission failure behavior.
- Latency from user request to model response.
- Cost per workflow and per active user.
- Log usefulness without leaking sensitive data.
- Recovery path for provider outage, quota exhaustion, or bad deploy.

## Debug Drill

Describe how you would troubleshoot a project where the app cannot call a model API.
