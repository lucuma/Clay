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
      ├── views/
      ├─────── static/
      └── settings.json

Inside that folder, run the development server with::

    $ clay run

and your site'll be available at ``http://0.0.0.0:5000/``.

Anything you put under ``views`` will be render as a page. For instance,
``views/page.html`` will be visible at::

    http://0.0.0.0:5000/page.html

and ``views/foo/bar.json`` at::

    http://0.0.0.0:5000/foo/bar.json


To generate a static version of your site, stop the server (with
``Control + C``) and run::

    $ clay build

and all the templates will be processed and the result stored inside the
``build`` folder.


How to install
--------------

Just run::

    sudo pip install clay

and you're ready to go.


Happy coding!
