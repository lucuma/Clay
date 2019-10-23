from pathlib import Path

import hecto
from pyceo import Manager
from pyceo import option
from pyceo import param

from clay.version import __version__


BLUEPRINT = (Path(__file__).parent / "blueprint").resolve()

m = Manager(f"<b>Clay v{__version__}")


@m.command(help="Creates a new Clay project at `path`.")
@param("path", help="Where to create the new project.")
@option("tmpl", help="Optional template to use to create the project.")
@option("quiet", help="Supress the status output.")
def new(path, tmpl=BLUEPRINT, **kwargs):
    """The `clay new` command creates a new Clay project with a default
    structure at the path you specify.

    You can also specify an optional project template as can be an absolute or
    relative path or a git URL. For the URLs, "gh:" works as a shortcut of
    "https://github.com/" and "gl:"as a shortcut of "https://gitlab.com/".

    Examples:

        # Render a sefault project to the "myapp/" folder
        clay new myapp

        # Custom template from an absolute or relative path.
        clay new myapp /path/to/project/template

        # Custom template from GitHub repo. Note the ".git" postfix.
        clay new myapp https://github.com/lucuma/clay-template.git

        # Custom template from the same GitHub repo with shortcut
        clay new myapp gh:/lucuma/clay-template.git

    """
    path = Path(path)
    print(path)
    print(tmpl)
    # hecto.copy(tmpl, path, **kwargs)


@m.command(help="Run Clay’s development server.")
@option("host", help="0.0.0.0 by default")
@option("port", type=int, help="8080 by default")
@option("path", help="Where to find the project. By default in the current folder.")
def run(host="0.0.0.0", port=8080, path="."):
    pass


@m.command(help="Generates a static copy of the project in a `build` folder.")
@option("path", help="Where to find the project. By default in the current folder.")
def build(path="."):
    pass


if __name__ == "__main__":
    m.run()
