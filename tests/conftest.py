from pathlib import Path
from tempfile import mkdtemp
import shutil

from webtest import TestApp
import pytest

from clay.main import Clay
from clay.server import make_app


@pytest.fixture()
def dst(request):
    """Return a real temporary folder path which is unique to each test
    function invocation. This folder is deleted after the test has finished.
    """
    dst = Path(mkdtemp()).resolve()
    request.addfinalizer(lambda: shutil.rmtree(str(dst), ignore_errors=True))
    return dst


@pytest.fixture()
def server(dst):
    clay = Clay(dst)
    app = make_app(clay)
    return TestApp(app)
