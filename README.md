
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

```
clay new myapp
```

will generate a new app container with the following structure::

    myapp
      ├── static/
      ├── clay.yml
      └── README.md


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

----

Happy coding!

