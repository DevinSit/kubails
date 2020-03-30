import logging
import sys
from functools import reduce, wraps
from shutil import which
from typing import Callable


logger = logging.getLogger(__name__)


def check_dependencies(*dependencies) -> Callable:
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _check_dependencies(*dependencies)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _check_dependencies(*dependencies) -> None:
    missing_deps = []

    for dep in dependencies:
        if which(dep) is None:
            missing_deps.append(dep)

    if len(missing_deps) > 0:
        missing_deps_string = reduce(lambda acc, dep: acc + "\n- {}".format(dep), missing_deps, "")

        print()
        logger.info("You are missing the following dependencies to run this command: \n{}".format(missing_deps_string))

        sys.exit(1)
