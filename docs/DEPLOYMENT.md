# Showcase Deployment

The showcase is a static app in this `docs/` folder. It can deploy through Vercel or GitHub Pages.

## Live URL

GitHub Pages:

```text
https://pablodcruz.github.io/ai-engineering-notebook/docs/
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
5. Replace the README showcase section with the production Vercel URL once the project URL is known.

The Vercel CLI is optional. If using it locally:

```bash
vercel
```

## GitHub Pages Deployment

GitHub Pages requires one repository setting before the workflow can succeed.

In GitHub:

1. Open repository settings.
2. Go to Pages.
3. Set the build and deployment source to GitHub Actions.
4. Run the `Deploy Showcase` workflow or push a change under `docs/`.

If the workflow fails at `Configure Pages`, the repository Pages source is not set to GitHub Actions yet, or Pages is not enabled for the repository.

## Local Preview

Open `docs/index.html` directly in a browser. No server, package install, or secrets are required.

## GitHub Pages Workflow

Workflow file:

```text
.github/workflows/deploy-showcase.yml
```

The workflow uploads the `docs/` folder as a GitHub Pages artifact and deploys it to the `github-pages` environment. If repository settings are configured to deploy from a branch instead of Actions, the same app is still available at `/docs/`.
