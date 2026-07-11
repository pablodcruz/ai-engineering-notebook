# Notebook Conventions

## Experiment Notes

Every lab or project should answer:

- What am I trying to learn or prove?
- What did I build?
- How do I run it?
- What broke?
- What did I change?
- What would I do differently in a production version?

## File Style

- Keep notes short and practical.
- Prefer examples over abstract claims.
- Capture errors and fixes while they are fresh.
- Link concepts to labs and projects.
- Avoid secrets, private context, and credential values.

## Artifact Levels

| Level | Meaning |
| --- | --- |
| Note | Rough understanding or reference. |
| Lab | Small reproducible exercise. |
| Project | Useful build with a demo path. |
| Showcase | Polished writeup or demo summary. |

## Status Language

Use a status that describes evidence, not ambition:

| Status | Meaning |
| --- | --- |
| Draft | Useful notes exist, but the artifact is not ready to follow end to end. |
| Scaffolded | Architecture and runnable pieces exist, but an important integration is simulated or unverified. |
| Runnable | A reviewer can execute the core behavior locally with documented steps. |
| Deploy-ready | Deployment configuration and controls exist, but the canonical live path has not been verified. |
| Live | The deployed path has been exercised and its public URL is documented. |
| Shipped | The milestone meets its stated definition of done and the workspace quality gate. |

## Generated Artifacts

Exported JSON and rendered reports must be reproducible from checked-in source data. When a source document changes, regenerate the affected export and run the full workspace validator before committing.

## Intentional Scaffolding

Templates and test fixtures may contain placeholders or minimal content because incompleteness is their purpose. Label them clearly and do not list them as demo-ready artifacts. Audit published notes, labs, projects, explainers, and navigation separately from scaffolding.
