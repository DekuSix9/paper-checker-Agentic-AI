import sys
import site
import os

# Insert user site-packages and current directory into sys.path
sys.path.insert(0, site.getusersitepackages())
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest

if __name__ == "__main__":
    exit_code = pytest.main(["tests/", "-v"])
    sys.exit(exit_code)
