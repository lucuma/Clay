from pathlib import Path
from tempfile import mkdtemp
import shutil

import pytest


@pytest.fixture()
def dst(request):
    """Return a real temporary folder path which is unique to each test
    function invocation. This folder is deleted after the test has finished.
    """
    dst = mkdtemp()
    dst = Path(dst).resolve()
    request.addfinalizer(lambda: shutil.rmtree(str(dst), ignore_errors=True))
    return dst
