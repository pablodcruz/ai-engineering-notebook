# Showcase Deployment

The repository has two complementary deployment surfaces. Vercel is the canonical runtime for the Support Triage Studio and its Python API functions. GitHub Pages hosts the static portfolio and credential-free recorded mirrors from `docs/`.

## Canonical Live Application

```text
https://ai-engineering-notebook.vercel.app/support-triage
```

Deployment health (configuration presence only; no billable model call):

```text
https://ai-engineering-notebook.vercel.app/api/health
```

## Static Portfolio

GitHub Pages:

```text
https://pablodcruz.github.io/ai-engineering-notebook/docs/
```

StreamFlow analytics dashboard:

```text
https://pablodcruz.github.io/ai-engineering-notebook/docs/streamflow-dashboard.html
```

## Vercel Deployment

The repository includes a root [vercel.json](../vercel.json) file with:

- `framework: null` for Vercel's "Other" framework preset.
- `outputDirectory: "docs"` so the rendered site is served from the static showcase folder.
- No install or build command because the app is plain HTML, CSS, and JavaScript.

Deploy flow:

1. Click the Vercel deploy button in the root README.
2. Import `pablodcruz/ai-engineering-notebook`.
3. Keep the root directory as the repository root.
4. Deploy.
5. Set the environment variables in `.env.example`, using secret values only in Vercel.
6. Run the health check, then make one allowlisted live request to verify the full provider path.

The Vercel CLI is optional. If using it locally:

```bash
vercel
```

## GitHub Pages Deployment

The current public URL shape includes `/docs/`, which means GitHub Pages is serving the repository root and the static showcase folder is part of the path.

The included workflow can also deploy the `docs/` folder as a Pages artifact. In that mode, files inside `docs/` are served from the site root instead, so the dashboard URL becomes:

```text
https://pablodcruz.github.io/ai-engineering-notebook/streamflow-dashboard.html
```

To use the workflow deployment mode, GitHub Pages requires one repository setting before the workflow can succeed.

In GitHub:

1. Open repository settings.
2. Go to Pages.
3. Set the build and deployment source to GitHub Actions.
4. Run the `Deploy Showcase` workflow or push a change under `docs/`.

If the workflow fails at `Configure Pages`, the repository Pages source is not set to GitHub Actions yet, or Pages is not enabled for the repository.

## Local Preview

Open `docs/index.html` directly for the static portfolio and recorded experiences. No server, package install, or secrets are required. Testing the live API locally requires the Vercel development server and the documented environment variables.

## GitHub Pages Workflow

Workflow file:

```text
.github/workflows/deploy-showcase.yml
```

The workflow uploads the `docs/` folder as a GitHub Pages artifact and deploys it to the `github-pages` environment. Because `docs/` is uploaded as the artifact root, files inside `docs/` are served from the site root when GitHub Pages is configured to deploy from GitHub Actions.
