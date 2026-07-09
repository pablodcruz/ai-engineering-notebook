# Resource Log

Track useful resources here as you study. Prefer official docs, primary sources, and high-quality engineering writeups.

| Date | Resource | Topic | Key Takeaway | Follow-Up |
| --- | --- | --- | --- | --- |
| 2026-07-09 | [actions/setup-python README](https://github.com/actions/setup-python) | GitHub Actions Python CI | Current examples use `actions/checkout@v6` and `actions/setup-python@v6`, with explicit Python versions recommended. | Keep CI action versions current during maintenance passes. |
| 2026-07-09 | [actions/deploy-pages README](https://github.com/actions/deploy-pages) and [actions/upload-pages-artifact README](https://github.com/actions/upload-pages-artifact) | GitHub Pages deployment | Pages deployment uses an uploaded artifact and requires `pages: write` plus `id-token: write` permissions. | Verify the repository Pages source is set to GitHub Actions before relying on automatic deployment. |

## Resource Quality Checklist

- Is it official documentation, a primary source, or a trusted technical source?
- Is it current enough for the topic?
- Does it include runnable examples?
- Does it explain tradeoffs and limitations?
- Can you turn it into a lab, demo, or interview talking point?
