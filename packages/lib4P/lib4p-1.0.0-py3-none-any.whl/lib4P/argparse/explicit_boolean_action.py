import argparse


class ExplicitBooleanAction(argparse.Action):

    def __init__(self, option_strings, dest, nargs=None, type=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        if type is not None:
            raise ValueError("type not allowed")

        # Inspired by argparse.BooleanOptionalAction
        _option_strings = []
        for option_string in option_strings:
            _option_strings.append(option_string)

            if option_string.startswith('--'):
                option_string = '--no-' + option_string[2:]
                _option_strings.append(option_string)

        super().__init__(_option_strings, dest, nargs="?", **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        if not isinstance(value, str) and value is not None:
            raise TypeError(f"Argument with action 'ExplicitBooleanAction' must be of type {str} to be parsed, "
                            f"type {type(value)} found")

        if isinstance(value, str):
            value = value.lower()
        if value is None or value == "t" or value == "true":
            value = True
        elif value == "f" or value == "false":
            value = False
        else:
            raise argparse.ArgumentError(self,
                                         "Not explicit enough, argument must be one of the following "
                                         "values (case insensitive): ['t', 'true', 'f', 'false', None]")

        if option_string.startswith("--no-"):
            value = not value

        setattr(namespace, self.dest, value)
