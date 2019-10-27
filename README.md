
# Clay

[![Coverage Status](https://coveralls.io/repos/github/lucuma/clay/badge.svg?branch=master)](https://coveralls.io/github/lucuma/clay?branch=master) [![Tests](https://travis-ci.org/lucuma/clay.svg?branch=master)](https://travis-ci.org/lucuma/clay/)

**An amazing prototyping tool.**

With Clay you can forget about making changes to dozens of HTML files
just because you need to add a link in the footer.

You can also use it to prototype your AJAX-driven application or the
responses of sending forms, because it acts like a real server.


## Install

```
pip install clay
```


## Quickstart

```python
clay new myapp
```

will generate a new app container with the following structure:

```
myapp
  ├── static/
  ├── clay.yml
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

**Don't do it**. Is error-prone and could not worl if you do it in a base layout, for example. Always write the internal URLs using their path from the root of the project, like this:


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


## The `clay.yaml` file

If a YAML file named `clay.yaml` is found in the root of the project, it will be read and used for configuring Clay.

```yaml
# Shell-style patterns files/folders that must not be rendered.
exclude:
  - ".*"
  - ".*/*"
  - "_*"
  - "_*/*"
  - "*.txt"

# Shell-style patterns files/folders that *must be* rendered, even if
# they are in the exclude list
include:
  - "robots.txt"
  - "humans.txt"

```

----

Happy coding!

