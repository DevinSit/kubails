import inspect
import logging
import re
import sys
from functools import reduce, wraps
from shutil import which
from typing import Any, Callable, List, Type, TypeVar


logger = logging.getLogger(__name__)

# Inspiration for typing 'cls' taken from https://stackoverflow.com/a/56856290.
T = TypeVar("T")

APP_DEPENDENCIES = ("docker", "docker-compose", "gcloud", "git", "helm", "kubectl", "make", "terraform")


def check_dependencies(*class_dependencies) -> Callable:
    if len(class_dependencies) == 0:
        class_dependencies = APP_DEPENDENCIES

    def decorator(cls: Type[T]) -> Type[T]:
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            # Don't decorate private methods.
            if not name.startswith("_"):
                method_dependencies = _get_method_dependencies(cls, method, class_dependencies)
                setattr(cls, name, check_dependencies_for_function(*method_dependencies)(method))

        return cls

    return decorator


def check_dependencies_for_function(*dependencies) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            _check_dependencies(*dependencies)
            # return func(*args, **kwargs)

        return wrapper

    return decorator


def _check_dependencies(*dependencies) -> None:
    missing_deps = []

    for dep in dependencies:
        if which(dep) is None:
            missing_deps.append(dep)

    if len(missing_deps) > 0:
        missing_deps_string = reduce(lambda acc, dep: acc + "\n- {}".format(dep), missing_deps, "")
        logger.info("You are missing the following dependencies to run this command: \n{}".format(missing_deps_string))

        sys.exit(1)


def _get_method_dependencies(cls: Type[T], func: Callable, dependencies_filter) -> List[str]:
    source = inspect.getsource(func)

    service_calls = re.findall(r"self\.(\w*)\.", source)
    private_calls = re.findall(r"self\.(\_\w*)\(\)", source)

    for call in private_calls:
        private_method = getattr(cls, call)
        service_calls.extend(_get_method_dependencies(cls, private_method, dependencies_filter))

    service_calls = list(set(service_calls))
    service_calls = list(filter(lambda x: x in dependencies_filter, service_calls))

    return sorted(service_calls)
