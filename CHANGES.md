# Clay Changelog

## Version 2.4

- Dropped the Werkzeug's server for the more robust CherryPy's Server (Cheroot).

- Added pattern matching (UNIX style) to the lists of FILTER and IGNORE.

- Added pattern matching to the `active` helper function.

- You can now specify many url patterns as arguments in the `active` helper
  function without having to use a list. Eg:

    active('/url1/', '/url2/', '/url3/', partial=True)


## Version 2.3

- _index.txt lists all the pages that also would appear in _index.html.


## Version 2.1 - 2.2

- Several bugfixes


## Version 2.0

TDD rewrite. Most important new features:

- _index.html now is viewable in run mode.

- No need to filter non-html files. Only those ending in ".html" or ".tmpl" are processed as templates.

- Adaptative run port (if it is taken, Clay try to use the next one).

- The "not found" page now shows the real missing templates (it could be "imported" inside the current page).

