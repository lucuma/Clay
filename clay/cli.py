import proper_cli

from .main import BLUEPRINT, STATIC_FOLDER, Clay
from .server import make_app
from .utils import vcs
from .utils.blueprint_render import BlueprintRender
from .utils.make_matcher import make_matcher, no_filter


class ClayCLI(proper_cli.Cli):
    """Welcome to Clay"""

    def new(self, dest: str, tmpl: str = BLUEPRINT) -> None:
        """Creates a new Clay project at `dest`

        The `clay new` command creates a new Clay project with a default
        structure at the path you specify.

        Arguments:
        - dest: Where to create the new project.
        - tmpl: Optional template to use to create the project.

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
        repo_url = vcs.get_repo(tmpl)
        if repo_url:
            tmpl = vcs.clone(repo_url)

        render = BlueprintRender(
            tmpl,
            dest,
            must_filter=no_filter,
            is_binary=make_matcher(("*.ico",)),
            static_folder=STATIC_FOLDER,
            block_start_string="[%",
            block_end_string="%]",
            variable_start_string="[[",
            variable_end_string="]]",
        )
        render(name=dest)

        print(f"\n Done! Now go to the `{dest}` folder")
        print(" and do `clay run` to start the server.\n")

    def run(
        self, host: str = "0.0.0.0", port: int = 8080, source: str = "."
    ) -> None:  # pragma: no cover
        """Runs Clay development server.

        Arguments:
        - host: 0.0.0.0 by default
        - port: 8080 by default
        - source: Where to find the project. By default in the current folder.
        """
        clay = Clay(source)
        app = make_app(clay)
        app.run(host, port)

    def build(self, source: str = ".") -> None:
        """Generates a static copy of the project in a `build` folder.

        Arguments:
        - source: Where to find the project. By default in the current folder.
        """
        clay = Clay(source)
        clay.build()
        print("\n Done! You'll find a static version of your ")
        print(" project in the `build` folder.\n")

    def pages(self, source: str = ".") -> None:
        """Prints a list of the available pages

        Arguments:
        - source: Where to find the project. By default in the current folder.
        """
        clay = Clay(source)
        pages = clay.list_pages()
        for page in pages:
            print(page)


cli = ClayCLI()
