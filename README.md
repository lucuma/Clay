# Clay

[![Build Status](https://travis-ci.org/lucuma/Clay.png)](https://travis-ci.org/lucuma/Clay)

**An amazing prototyping tool.**

http://lucuma.github.com/Clay

With Clay you can forget about making changes to dozens of HTML files just because you need to add a link in the footer.

You can also use it to prototype your AJAX-driven application or the responses of sending forms, because it acts like a real server.


## Instructions

Run the development server with

    $ clay run

or generate a static version of the site

    $ clay build


## Quickstart


    $ clay new myappname

will generate a new app container with the following structure::

    myappname
      ├── source/
      ├─────── static/
      ├── README.md
      └── settings.py

Inside that folder, run the development server with:

    $ clay run

and your site'll be available at `http://localhost:8080/`.

Anything you put under `source` will be render as a page. For instance `source/page.html` will be visible at `http://localhost:8080/page.html`, and `source/foo/bar.json` at `http://localhost:8080/foo/bar.json`.

To generate a static version of your site, stop the server (with `Control + C`) and run:

    $ clay build

and all the templates will be processed and the result stored inside the `build` folder.

## Settings

Since latest versions Clay uses a `settings.py` file which is considered as a full python module.
Warning: This file is not created yet by template, so you have to create it yourself (and ignore or delete `settings.yml` file)


Example::

    FILTER_PARTIALS=True
    FILTER=['base.html']
    INCLUDE=[]
    
    host='0.0.0.0'
    port=8080

In case you are including a template you don't want to be "browseable", just included you can make this::


    FILTER=['base.html', 'footer.html']


This also solves a `variable not found error` when using variables inside included templates.

For an advanced settings example see Issue #16


## How to install

Just run

    sudo pip install clay

and you're ready to go.


## Templates

The real power of Clay comes by using the Jinja2 template syntax. 

You can make a single file, (for instance, your header) and included it many times using:
    
    {% include "header.html "%}

You can also use a powerful feature called _template inheritance_: inside the `source` folder you'll find a file called `base.html`. This is a page skeleton shared among the rest of HTML templates. You put in there anything you want to be repeated in every page, like the doctype declaration or maybe navigation links and a footer. You change something there and the rest of the pages will be automatically updated. Much more easy than manually search and replace a bunch of files!

The rest of the files, like `index.html`, are composed of **blocks**, like

    {% block title %}Welcome to Clay{% endblock %}

Any content you put *inside* those blocks will be used to fill the same-named blocks in `base.html`. In this case to fill the `<title>` tag.

You can create new blocks for your templates. You can even create new base files, just change in your templates the base that they will use, by updating the line that says:

    {% extends "base.html" %}

You can use more than just HTML: JSON, csv, plain text, etc. Any text-based format will be ok.

Jinja2 templates are much more than just template inheritance. For more advaced features check the [official documentation] (http://jinja.pocoo.org/docs/templates/).


---------------------------------------
***Happy coding!***


---------------------------------------
© [Lúcuma] (http://lucumalabs.com).<br />
See `AUTHORS.md` for more details.<br />
License: [MIT License] (http://www.opensource.org/licenses/mit-license.php).
