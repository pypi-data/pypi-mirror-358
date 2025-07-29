from .parser_interface import ParserInterface

_register = dict()


def register(name, version, parser, override=False):
    global _register

    check_name(name)
    if isinstance(version, str):
        version = parse_version(version)
    check_version(version)
    check_parser(parser)

    if name not in _register:
        _register[name] = dict()

    if version not in _register[name] or override:
        _register[name][version] = parser
    else:
        raise KeyError("A parser already exists for the specified name and version."
                       "[inadvisable] If you really want to override the existing parser, use the `override` argument.")


def get_parser(name="default", version=None):
    global _register

    check_name(name)
    if version is not None:
        if isinstance(version, str):
            version = parse_version(version)
        check_version(version)

    if name not in _register:
        return None

    matching_version = find_matching_version(version, _register[name].keys())

    if matching_version is None:
        return None

    return _register[name][matching_version]


def is_valid_name(name):
    return isinstance(name, type) or (isinstance(name, str) and name != "")


def is_valid_version(version):
    return isinstance(version, tuple) and len(version) == 3 and all(isinstance(value, int) for value in version)


def check_name(name):
    if not is_valid_name(name):
        raise ValueError("name must be a string and not empty")


def check_version(version):
    if not is_valid_version(version):
        raise ValueError("version must be a tuple of 3 integer values")


def check_parser(parser):
    if not isinstance(parser, ParserInterface):
        raise ValueError(f"parser must inherit from the {ParserInterface} class")


def parse_version(version):
    if is_valid_version(version):
        return version

    if not isinstance(version, str):
        raise TypeError(f"Can only parse versions of type {str}")

    values = version.split(".")

    if len(values) != 3 or not all(value.isdigit() for value in values):
        raise ValueError("Cannot parse the version, the version variable must be composed of 3 integers "
                         "separated by dots (eg: '1.0.0').")

    return tuple(int(value) for value in values)


def find_matching_version(version, version_list):
    if version is not None:
        check_version(version)
    if len(version_list) == 0:
        raise ValueError("Argument 'version_list' must not be empty")
    if not all(is_valid_version(available_version) for available_version in version_list):
        raise ValueError("At least one item in 'version_list' is not a valid version")

    version_list = sorted(version_list)

    if version is None:
        return version_list[-1]

    if version < version_list[0]:
        return None

    latest_compatible_version = version_list[0]
    for available_version in version_list:
        if available_version > version:
            break
        else:
            latest_compatible_version = available_version
    return latest_compatible_version


def get_latest_version():
    global _register

    return max([version for versions in _register.values() for version in versions.keys()])

def does_version_exists(version):
    check_version(version)
    return version in {version for versions in _register.values() for version in versions}