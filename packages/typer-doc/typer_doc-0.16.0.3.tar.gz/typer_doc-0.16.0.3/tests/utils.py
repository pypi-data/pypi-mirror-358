import shutil
import sys
from os import getenv

import pytest

try:
    import shellingham
    from shellingham import ShellDetectionFailure

    shell = shellingham.detect_shell()[0]
except ImportError:  # pragma: no cover
    shellingham = None
    shell = None
except ShellDetectionFailure:  # pragma: no cover
    shell = None


needs_py310 = pytest.mark.skipif(
    sys.version_info < (3, 10), reason="requires python3.10+"
)

needs_linux = pytest.mark.skipif(
    not sys.platform.startswith(("linux", "darwin")), reason="Test requires Linux/macOS"
)

needs_bash = pytest.mark.skipif(
    shutil.which("bash") is not None, reason="Test requires Bash"
)

requires_completion_permission = pytest.mark.skipif(
    not getenv("_TYPER_RUN_INSTALL_COMPLETION_TESTS", False),
    reason="Test requires permission to run completion installation tests",
)
