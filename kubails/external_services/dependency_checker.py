import inspect
import logging
import re
import sys
from functools import reduce, wraps
from shutil import which
from typing import Any, Callable, List, Type, TypeVar


logger = logging.getLogger(__name__)

# Method for typing 'cls' taken from https://stackoverflow.com/a/56856290.
T = TypeVar("T")

# These are the global app dependencies. While classes can declare their own dependencies through the decorator,
# it's best just to use these defaults because then they only have to be updated in one place.
APP_DEPENDENCIES = ("docker", "docker-compose", "gcloud", "git", "helm", "kubectl", "make", "terraform")


def check_dependencies(*class_dependencies) -> Callable:
    """
    Applies a decorator to all the public methods of a class that verifies the method's
    necessary dependencies are installed before running the method.

    @param class_dependencies   A whitelist of dependencies that the entire class uses.
                                Used to ensure a method's dependencies only come from this list.

    @return The decorator function for a class.
    """
    # Since we can't set the default value of an unpacked arg list in the function definition, we set it here.
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
            missing_deps = _get_missing_dependencies(*dependencies)

            if len(missing_deps) > 1:
                logger.debug("Required dependencies: {}".format(dependencies))

                missing_deps_string = reduce(lambda acc, dep: acc + "\n- {}".format(dep), missing_deps, "")
                logger.info(
                    "You are missing the following dependencies to run this command: \n{}".format(missing_deps_string)
                )

                sys.exit(1)
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


def _get_missing_dependencies(*dependencies) -> List[str]:
    # Use 'which' (like, the bash 'which') to check if the dependency is installed.
    return [dep for dep in dependencies if which(dep) is None]


def _get_method_dependencies(cls: Type[T], func: Callable, dependencies_filter) -> List[str]:
    """
    Determines all of a given method's dependencies that fall within the dependencies_filter.

    Directly examines the source code for the method (and that of others on the class) to
    determine the dependencies.

    Yes, it's pretty jank that we're doing this by inspecting source code and using regex,
    _but it works!_ (for now...)

    @param cls      The class that the func originates from.
    @param func     The method to determine the dependencies for.
    @param dependencies_filter  The whitelist of valid dependencies.
    """
    source = inspect.getsource(func)

    # This first regex matches all public, instance methods
    # (i.e. everything between "self." and ".").
    # e.g. "self.terraform.get_cluster_name()" matches "terraform".
    #
    # The parentheses in the regex are a 'capturing group'.
    #
    # This only works for finding 'service' calls because all of our external_services
    # are registered as public instance methods as part of the constructor for each service.
    service_calls = re.findall(r"self\.(\w*)\.", source)

    # This second regex matches all private, instance methods
    # (i.e. everything between "self." and "()", including an underscore).
    # e.g. "self._deploy_storage_classes()" matches "_deploy_storage_classes".
    #
    # The parentheses in the regex are a 'capturing group'.
    private_calls = re.findall(r"self\.(\_\w*)\(\)", source)

    # Now we have to dive into the source of the private calls to find any service calls that they use.
    # Obviously, this is done recursively. As such, there is the possibility that this just loops
    # infinitely if there is something like a recursive call of a private method in a private method.
    # But we take those risks!
    for call in private_calls:
        private_method = getattr(cls, call)
        service_calls.extend(_get_method_dependencies(cls, private_method, dependencies_filter))

    # Remove duplicates.
    service_calls = list(set(service_calls))

    # Ensure only dependencies from the dependencies_filter are kept.
    service_calls = list(filter(lambda x: x in dependencies_filter, service_calls))

    # Sort the dependencies for the user's benefit.
    return sorted(service_calls)
