import hecto
from pyceo import Manager
from pyceo import option
from pyceo import param

from .main import Clay, BLUEPRINT
from .server import make_app
from .version import __version__


cli = Manager(f"<b>Clay v{__version__}", catch_errors=False)


@cli.command(help="Creates a new Clay project at `dest`.")
@param("dest", help="Where to create the new project.")
@option("tmpl", help="Optional template to use to create the project.")
@option("quiet", help="Supress the status output.")
def new(dest, tmpl=BLUEPRINT, quiet=False):
    """The `clay new` command creates a new Clay project with a default
    structure at the path you specify.

    You can also specify an optional project template as can be an absolute or
    relative path or a git URL. For the URLs, "gh:" works as a shortcut of
    "https://github.com/" and "gl:"as a shortcut of "https://gitlab.com/".

    Examples:

        # Render a default project to the "myapp/" folder
        clay new myapp

        # Custom template from an absolute or relative path.
        clay new myapp /path/to/project/template

        # Custom template from GitHub repo. Note the ".git" postfix.
        clay new myapp https://github.com/lucuma/clay-template.git

        # Custom template from the same GitHub repo with shortcut
        clay new myapp gh:/lucuma/clay-template.git

    """
    hecto.copy(tmpl, dest, quiet=quiet)
    print(f"\n Done! Now go to the `{dest}` folder")
    print(" and do `clay run` to start the server.\n")


@cli.command(help="Run Clay’s development server.")
@option("host", help="0.0.0.0 by default")
@option("port", type=int, help="8080 by default")
@option("source", help="Where to find the project. By default in the current folder.")
def run(host="0.0.0.0", port=8080, source="."):  # pragma: no cover
    clay = Clay(source)
    app = make_app(clay)
    app.run(host, port)


@cli.command(help="Generates a static copy of the project in a `build` folder.")
@option("source", help="Where to find the project. By default in the current folder.")
@option("quiet", help="Supress the status output.")
def build(source=".", quiet=False):
    clay = Clay(source)
    clay.build(quiet=quiet)
    print("\n Done! You'll find a static version of your ")
    print(f" project in the `build` folder.\n")



@cli.command(help="Return a list of the available pages")
@option("source", help="Where to find the project. By default in the current folder.")
def pages(source="."):
    clay = Clay(source)
    pages = clay.list_pages()
    for page in pages:
        print(page)


def run_cli():  # pragma: no cover
    cli.run()
