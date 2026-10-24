# Data Science Looks at Discrimination

*A toolkit for investigating bias in race, gender, age and so on*

[Read the book](https://matloff.github.io/dsldBook/).

This book covers two major aspects of the use of data science in
discrimination contexts:

* **Part I:**  Assessing possible discrimination in observational
  contexts.

* **Part II:** Ameliorating discrimination in machine learning
  applications.

The book makes extensive use of the [dsld R
package](https://github.com/matloff/dsld), and is best read with access
to that software. However, its conceptual content is quite accessible
independently of that package.

## Read locally

The rendered HTML is included in `docs/`. With Python 3 installed:

```sh
make serve
```

Open <http://127.0.0.1:8765>. Use `make serve PORT=8766` to choose another
port. The book's scripts, styles, fonts, and math renderer are served locally.

## Build

Install [Quarto](https://quarto.org/docs/get-started/), R, and the R packages
`knitr`, `rmarkdown`, `dsld`, `qeML`, and `fairness`, including their dependencies.
The verified build environment uses Quarto 1.10.19, R 4.5.1, dsld 1.0.0,
qeML 1.1, knitr 1.50, and rmarkdown 2.29.

```sh
make html
make check
```

`make preview` rebuilds the HTML as sources change and serves it locally.
The Makefile uses `quarto` on `PATH`, or `.tools/bin/quarto` when available.
Set `QUARTO=/path/to/quarto` to use a specific installation.

The R examples can take several minutes to execute. Cached results speed up
subsequent renders. After changing packages or shared R setup, rerun all
enabled examples:

```sh
make rebuild
```

## Project layout

| Path | Contents |
| --- | --- |
| `*.qmd` | Book chapters in Quarto Markdown. |
| `_quarto.yml` | Chapter order, execution settings, and HTML configuration. |
| `assets/authors/` | Author portraits. |
| `assets/figures/` | Book illustrations. |
| `assets/styles.css` | Reading layout and responsive portrait styles. |
| `assets/vendor/` | KaTeX, fonts, and third-party license information. |
| `docs/` | Generated HTML for GitHub Pages. |
| `tools/` | Local preview and validation commands. |

Edit the chapter sources and assets, then rebuild `docs/`; do not edit the
rendered HTML directly. Keep chapter filenames and section IDs stable so
existing links continue to work. Local tools, caches, and validation output
are ignored by Git.

## Validate and publish

`make check` validates local links, section anchors, filename casing, image
and font paths, and the search index.

For browser validation, install Node.js and Playwright:

```sh
npm install --prefix .tools/browser playwright@1.62.1
.tools/browser/node_modules/.bin/playwright install chromium
```

With `make serve` running in another terminal:

```sh
make check-browser
```

This checks all chapters at desktop, tablet, and phone widths (320–1440px),
including images, math rendering, JavaScript errors, and page overflow. External requests are
blocked during the check. Reports and screenshots are saved in `.build/qa/`.
Set `BOOK_URL` for another preview address or `CHROMIUM_EXECUTABLE` to use
an existing Chromium executable.

Before publishing, run `make rebuild`, `make check`, and `make check-browser`,
and review the rendered pages. Commit the source changes together with the
rebuilt `docs/` directory. GitHub Pages publishes `docs/` from `main`.

## License

This work is licensed under a Creative Commons Attribution-No Derivative Works 3.0 United States License. Copyright is retained in all non-U.S. jurisdictions, but permission to use these materials in teaching is still granted, provided the authorship and licensing information here is displayed.
