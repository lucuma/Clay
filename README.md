
# Clay

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


## Build version

To generate a static version of your site, first, stop the server with
``Control + C``, and then run:

```
clay build
```

and all the templates will be processed and the result stored inside the
`build` folder.


## The clay.yaml file

If a YAML file named `clay.yaml` or `clay.yml` is found in the root of the project, it will be read and used for configuring Clay.

```yaml
# Shell-style patterns files/folders that must not be rendered.
exclude:
  - "_*.*"
  - "*.txt"
  - ".git"
  - ".git/*"

# Shell-style patterns files/folders that *must be* rendered, even if
# they are in the exclude list
include:
  - "robots.txt"
  - "humans.txt"

```

----

Happy coding!

