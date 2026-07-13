# Mocked Zendesk-Style Support Adapter

A credential-free integration prototype that turns signed, synthetic support-platform webhooks
into normalized triage inputs and proposed-only ticket updates.

## Run The Tests

```powershell
python -m unittest discover -s tests
```

## Refresh Recorded Evidence

From the repository root:

```powershell
python scripts\export_support_adapter.py
python scripts\export_support_adapter.py --check
```

The implementation is in `src/support_adapter/adapter.py`. It has no third-party runtime
dependencies and never calls Zendesk, a model provider, or another external service.

See the [complete project record](../zendesk-style-support-adapter.md) and
[deployed trace viewer](../../docs/support-adapter.html).
