# Commonplace

A simple, responsive study-notes website made for GitHub Pages. It is a lightweight, static interpretation of the study-notes project in this repository.

## Open the website

Open `site/index.html` in a browser, or run a local server from the repository root:

```sh
python3 -m http.server 3000 --bind 0.0.0.0 --directory site
```

Then visit `http://localhost:3000`. No package installation or build step is needed.

## What works

- Six readable starter notes across Maths, Physics, Chemistry, and Computer Science.
- Search by title, subject, or note content.
- Subject filters and a saved-notes view.
- Bookmarks stored locally in the current browser, with an in-memory fallback if storage is unavailable.
- Individual note links such as `site/index.html#note/quadratic-equations`.
- A random-note picker, keyboard-accessible reading dialog, and mobile navigation.
- Responsive layouts and reduced-motion support.

The starter notes are example educational content, not live user submissions. There is no login, database, analytics, or shared publishing backend. Bookmarks are not synced between devices. The original ZIP archive is left unchanged.

## Make it your own

- Edit `site/notes.js` to add or change notes. Each note needs a unique, URL-friendly `id`, a supported subject, a title, summary, reading time, and sections.
- Edit `site/index.html` for the site name, introduction, and links.
- Edit `site/styles.css` for colors, fonts, and layout.
- The site uses local files and system fonts only; it does not depend on a CDN.

To add a subject, add its label/icon to `subjects` in `site/app.js`, a filter button in `site/index.html`, and its colors in `site/styles.css`.

## Publish on GitHub Pages

The included `.github/workflows/static.yml` publishes **only the `site` directory** when changes reach `main`.

1. Push this branch and merge it into `main` (or open a pull request and merge that).
2. In the GitHub repository, open **Settings → Pages**.
3. Under **Build and deployment**, choose **GitHub Actions** as the source.
4. Open **Actions → Deploy static content to Pages** to follow the deployment. You can also run it manually with **Run workflow**.
5. When the deployment succeeds, the workflow shows the public website URL. For this repository, the expected URL is `https://minzritesh43-coder.github.io/ritesh_/`.

The current Arena working branch is not automatically published by this workflow. Merging into `main` is required for automatic deployment. All asset paths are relative, so the website also works under the repository's Pages subpath.
