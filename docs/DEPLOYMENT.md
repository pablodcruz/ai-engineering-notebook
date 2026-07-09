# Showcase Deployment

The showcase is a static app in this `docs/` folder. It is designed to deploy through GitHub Pages with GitHub Actions.

## Required Repository Setting

In GitHub:

1. Open repository settings.
2. Go to Pages.
3. Set the build and deployment source to GitHub Actions.
4. Run the `Deploy Showcase` workflow or push a change under `docs/`.

If the workflow fails at `Configure Pages`, the repository Pages source is not set to GitHub Actions yet, or Pages is not enabled for the repository.

## Local Preview

Open `docs/index.html` directly in a browser. No server, package install, or secrets are required.

## Deployment Workflow

Workflow file:

```text
.github/workflows/deploy-showcase.yml
```

The workflow uploads the `docs/` folder as a GitHub Pages artifact and deploys it to the `github-pages` environment.
