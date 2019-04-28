"""
The first-run configuration file for PyTest. PyTest runs the code in this file before any tests.
So far, this is just used to set a flag so that code can check whether or not it's running in a test
(used to disable the file logger when testing).
For more information about conftest.py, see https://docs.pytest.org/en/2.7.3/plugins.html.
"""

import sys


def pytest_configure(config):
    sys._called_from_test = True
