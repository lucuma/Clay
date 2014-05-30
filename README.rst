========
Clay
========

**A rapid prototyping tool.**

With Clay you can forget about making changes to dozens of HTML files
just because you need to add a link in the footer.
 
You can also use it to prototype your AJAX-driven application or the
responses of sending forms, because it acts like a real server.

Quickstart
----------

::

    $ clay new myappname

will generate a new app container with the following structure::

    myappname
      ├── source/
      ├─────── static/
      ├── README.md
      └── settings.py

Inside that folder, run the development server with::

    $ clay run

and your site'll be available at ``http://0.0.0.0:8080/``.

Anything you put under ``source`` will be render as a page. For instance,
``source/page.html`` will be visible at::

    http://0.0.0.0:8080/page.html

and ``source/foo/bar.json`` at::

    http://0.0.0.0:8080/foo/bar.json


To generate a static version of your site, stop the server (with
``Control + C``) and run::

    $ clay build

and all the templates will be processed and the result stored inside the
``build`` folder.

Settings
--------
Since latest versions Clay uses a settings.py file which is considered as a full python module.
Warning: This file is not created yet by template, so you have to create it yourself (and ignore or delete settings.yml file)


Example:

```
FILTER_PARTIALS=True
FILTER=['base.html']
INCLUDE=[]

host='0.0.0.0'
port=8080
```

In case you are including a template you don't want to be "browseable", just included you can make this:


```
FILTER=['base.html', 'footer.html']
```

This also solves a *variable not found error* when using variables inside included templates.

For an advanced settings example see Issue #16

How to install
--------------

Just run::

    sudo pip install clay

and you're ready to go.


Happy coding!
