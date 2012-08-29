# Clay Changelog


## Version 1.1

- All markdown meta data is now processed as markdown source.

- Improved CodeHtmlFormatter for the pygments extension. Now generates `<pre><code class="highlight _language_">` instead of `<div class="highlight _language_"><pre>`.

- Local Request instance even when building views (so 'request.path` works now).

- Fix bug with custom settings being overwritten by the default ones.

- Fix a bug with the markdown plugin while searching automatically for the first header.

- Clay now runs on Windows.

- Removed typographer extension.
