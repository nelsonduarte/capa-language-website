# capa-language-website

The marketing + learn-the-language site for [Capa](https://github.com/nelsonduarte/capa-language).
Served at [`capa-language.com`](https://capa-language.com) via
GitHub Pages from the `main` branch root.

## Layout

```
index.html         landing page
why.html           the pitch
compare.html       positioning vs adjacent languages and claim sources
start.html         install + first program
migrating.html     gradual migration from Python
manifest.html      capability manifest deep-dive
regulatory.html    CRA / NIS2 / DORA / SSDF / SCVS mapping
agent-demo.html    capability-bound LLM agent showcase
reference.html     language reference (rendered)
stdlib.html        standard library reference
roadmap.html       project roadmap (rendered)
brand.html         logo + brand guidelines
community.html     where to ask + contribute
learn/             14-chapter tutorial sequence
style.css          single stylesheet, light + dark modes
theme.js           light/dark toggle + persistence
favicon.svg        site icon
capa_logo.png      OG image / fallback
capa_logo.svg      vector logo
sitemap.xml        sitemap
robots.txt         crawler rules
CNAME              capa-language.com (GitHub Pages custom domain)
```

Deeper Markdown documents (semantics, packages, regulatory
mapping, CVE case studies, paper draft) live in the main Capa
repo's [`docs/`](https://github.com/nelsonduarte/capa-language/tree/main/docs)
folder and are linked from this site via absolute GitHub URLs.
The split keeps the website source small and the documents
near the code they describe.

## Local preview

The site is pure static HTML/CSS/JS; no build step.

```bash
git clone https://github.com/nelsonduarte/capa-language-website
cd capa-language-website
python -m http.server 8000
# open http://localhost:8000
```

## Editing

Pages are hand-written HTML. The repo deliberately avoids a
static-site generator: no Jekyll `_config.yml`, no Hugo, no
Eleventy. The footprint is small enough that hand-editing is
faster than templating, and the diff in `git log -p` reads as
prose.

Style conventions:

- Section headers use `<h2>`; sub-headers `<h3>`. `<h1>` is the
  page title only, used once per page.
- Code blocks: triple-backticks render as `<pre><code>`; no
  syntax highlighter (small enough samples that the contrast
  loss is not worth a JS dependency).
- Internal links: relative paths (e.g. `start.html`). External
  links to the main repo: absolute
  `https://github.com/nelsonduarte/capa-language/...`.

## Provenance

This repo was extracted from
[`nelsonduarte/capa-language`](https://github.com/nelsonduarte/capa-language)
on 2026-05-23 via `git filter-repo` so the per-file `git log`
history is intact. The earliest commits in this history are
the original website-only commits from the main repo.

## License

Dual MIT OR Apache-2.0, matching the parent repo. See
[`LICENSE-MIT`](LICENSE-MIT) and [`LICENSE-APACHE`](LICENSE-APACHE).
