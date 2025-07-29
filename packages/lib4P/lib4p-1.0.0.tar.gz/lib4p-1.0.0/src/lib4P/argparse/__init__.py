import argparse
import sys

from .explicit_boolean_action import ExplicitBooleanAction


class ArgumentParser(argparse.ArgumentParser):
    """
    Overlay of the argparse module.

    It requires defining the name (`prog`), the `description` and the `version` of the module to be clean and complete,
    and to be reused later for various purposes (standardization of logs, etc.)
    """

    def __init__(self, prog, description, version, formatter_class=argparse.ArgumentDefaultsHelpFormatter, *args, **kwargs):
        """
        See :class:`argparse.ArgumentParser`.
        """
        super(ArgumentParser, self).__init__(prog=prog, description=description, formatter_class=formatter_class, *args, **kwargs)
        self.add_argument("--version", action="version", version=version)

        self._args_in_processing = None

    def print_processed_args(self, file=None):
        """
        Print the last arguments passed and processed in the :py:meth:`parse_args method`.
        Useful for indicating the arguments received, especially in case of an error during parsing.

        :param file: the output or output file (default: stdout)
        :type file: IO[str] | None
        """
        if file is None:
            file = sys.stdout
        self._print_message(f"module executed with arguments: {self._args_in_processing}\n", file)

    def parse_args(self, args=None, **kwargs):
        """
        Overload the original function to capture passed arguments (reused in :py:meth:`print_processed_args`).

        See :class:`argparse.ArgumentParser`.
        """
        self._args_in_processing = sys.argv[1:] if args is None else args
        return super().parse_args(args, **kwargs)

    def error(self, message):
        """
        Overload the original function to capture passed arguments (reused in :py:function:`print_processed_args`).

        See :class:`argparse.ArgumentParser`.
        """
        self.print_processed_args(file=sys.stderr)
        super().error(message)
