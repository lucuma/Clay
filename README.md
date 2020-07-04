
# Clay

[![Coverage Status](https://coveralls.io/repos/github/lucuma/Clay/badge.svg?branch=clay3)](https://coveralls.io/github/lucuma/Clay?branch=clay3) [![Tests](https://travis-ci.org/lucuma/Clay.svg?branch=master)](https://travis-ci.org/lucuma/Clay/)

**An amazing prototyping tool.**

With Clay you can forget about making changes to dozens of HTML files
just because you need to add a link in the footer.

You can also use it to prototype your AJAX-driven application or the
responses of sending forms, because it acts like a real server.


## Install

```
pip install clay
```

Clay version 3.x only works with Python 3.6, 3.7, and 3.8.


## Quickstart

```python
clay new myapp
```

will generate a new app container with the following structure:

```
myapp
  ├── static/
  ├── clay.yaml
  └── ...other files
```

You can also use an optional project template path or git URL. For the URLs, "gh:" works as a shortcut of "https://github.com/" and "gl:"  as a shortcut of "https://gitlab.com/". For example:

```python
# Absolute or relative path.
clay new myapp /path/to/project/template

# GitHub repo. Note the ".git" postfix.
clay new myapp https://github.com/lucuma/clay-template.git

# The same GitHub repo with shortcut
clay new myapp gh:/lucuma/clay-template.git
```


## Development server

Inside that folder, run the development server with:

```
clay run
```

and your site'll be available at ``http://0.0.0.0:8080/``.

Anything inside the `static` folder is served as-is under the `/static/` path.
For example you can see `myapp/static/image.png` at the `http://0.0.0.0:8080/static/image.png` URL.

Any file outside the  `static` folder, is rendered as a page.

For example, `myapp/page.html` is rendered and shown at `http://0.0.0.0:8080/page.html`, as an HTML page.

And `myapp/foo/bar.json` is rendered and shown at `http://0.0.0.0:8080/foo/bar.json` as a JSON document.

Remember to put inside `static` anything you don't want to be rendered.


## Build version

To generate a static version of your site, first, stop the server with
``Control + C``, and then run:

```
clay build
```

and all the templates will be processed and the result stored inside the
`build` folder.



## Static files

If you have folders in your project, you might be tempted to write internal URLs like this

```html
<!-- DON'T DO THIS ->
href="../a.html"
src="../static/main.js"
```

**Don't do it**. Is error-prone and could not work as expected if you do it in a base layout, for example. Always write the internal URLs using their path from the root of the project, like this:


```html
href="/a.html"
src="/static/main.js"
```

That'll work on the development server and also when generating a static version of your site, Clay will convert them into relative paths automatically.


## Template globals

When writing your templates, in addition of what is normally available in [Jinja templates](https://jinja.palletsprojects.com/en/2.10.x/) you have access to some other helper functions:

- The python's functions `dir`, `enumerate`, `map`, `zip`, and `len`.
- The **`now`** function, as an alias to `datetime.datetime.utcnow`.
- The **`active`** function, to set an "active" class in navigations/menus when the current page match.

### `active()`

```python
active(*url_patterns, partial=False, class_name="active")
```

TODO


## The `clay.yaml` file

If a YAML file named `clay.yaml` is found in the root of the project, it will be read and used for configuring Clay.

```yaml
---
# Shell-style patterns files/folders that must not be copied.
# Use quotes.
exclude:
  - ".*"
  - ".*/*"
  - "~*"
  - "~*/*"
  - "_*"
  - "_*/*"
  - "*.txt"

# Shell-style patterns files/folders that *must be* copied, even if
# they are in the exclude list.
# Use quotes.
include:
  - "robots.txt"
  - "humans.txt"

# Jinja extensions to use eg: `jinja2.ext.with_`
jinja_extensions:
  - jinja2.ext.with_

# Shell-style patterns of files outside `static/` that must be copied
# as-is instead of trying to interpret them as Jinja templates.
# Use quotes.
binaries:
  - "favicon.ico"
```


## Update from v2 to v3+

Before v3, previous versions of Clay did work with having all source files in a `source` subfolder. However, this is no longer the case, and the recommended setup is to have them in the parent folder instead.

The old project with a `source` folder still works, but it might change in future versions.


----

Happy coding!

