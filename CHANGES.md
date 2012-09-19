# Clay Changelog


## Version 1.3

- Fix bug that in some cases prevent it from running when some extra plugin libraries where missing.

- All settings names are upper cased by default (altough lower case versions are supported as well).

- Default jQuery updated to 1.8.1

- Merged a README typo fix by @z4y4ts (thanks).

## Version 1.2

- Several bug fixes

## Version 1.1

- All markdown meta data is now processed as markdown source.

- Improved CodeHtmlFormatter for the pygments extension. Now generates `<pre><code class="highlight _language_">` instead of `<div class="highlight _language_"><pre>`.

- Local Request instance even when building views (so 'request.path` works now).

- Fix bug with custom settings being overwritten by the default ones.

- Fix a bug with the markdown plugin while searching automatically for the first header.

- Clay now runs on Windows.

- Removed typographer extension.
