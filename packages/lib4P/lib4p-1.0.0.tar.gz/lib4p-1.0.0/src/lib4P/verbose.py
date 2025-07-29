__is_activated__ = False
"""
Flag indicating whether verbosity is enabled
"""

_print_function = print
"""
Function called to perform the display. Must take the string to be displayed as an argument.
"""

_function_input_string = "Executing function '{0}' with the following arguments:\n{1}"
"""
Schema of the string used at the function input. (0: function name, 1: input arguments, 2: output value)
"""

_function_output_string = "Function '{0}' output: {2}"
"""
Schema of the string used at the function output. (0: function name, 1: input arguments, 2: output value)
"""



def activate():
    """
    Enables verbosity on functions with the 'verbosify' decorator.
    """
    global __is_activated__
    __is_activated__ = True


def deactivate():
    """
    Disables verbosity on functions with the 'verbosify' decorator.
    """
    global __is_activated__
    __is_activated__ = False


def is_activated():
    """
    Indicates whether verbosity is enabled or not.

    :return: True if verbosity is enabled, False otherwise
    :rtype: bool
    """
    return __is_activated__


def set_print_function(function):
    """
    Sets the function used to perform verbosity display.

    :param function: Function used to perform verbosity display. Must be callable and take the string to be displayed directly as input.
    :type function: function
    """
    if not callable(function):
        raise TypeError("Argument 'function' must be callable")
    global _print_function
    _print_function = function

def set_function_input_string(input_string):
    """
    Sets the string used as the input to the function containing the decorator. The string is formatted with:
        - 0: function name
        - 1: input argument(s)
        - 2: output value(s)
    """
    global _function_input_string
    _function_input_string = input_string

def set_function_output_string(output_string):
    """
    Sets the string used as the output to the function containing the decorator. The string is formatted with:
        - 0: function name
        - 1: input argument(s)
        - 2: output value(s)
    """
    global _function_output_string
    _function_output_string = output_string


def verbosify(function):
    """
    Decorator to add verbosity to the use of a function.
    By specifying this decorator, and enabling verbosity (see the activate() function), the input arguments and output
    of the function will be displayed in the standard output.

    :param function: the function to wrap
    :type function: function
    :return: the function wrapped in the decorator
    :rtype: function
    """
    def wrapper(*args, **kwargs):
        if __is_activated__:
            output=None
            str_args = "\n".join(["\t"+str(key)+": "+str(value.__repr__()) for key, value in dict(zip(function.__code__.co_varnames, args)).items()]
                                 + ["\t"+str(key)+": "+str(value.__repr__()) for key, value in kwargs.items()])
            a=_function_input_string.format(function.__name__, str_args, output)
            _print_function(_function_input_string.format(function.__name__, str_args, output))
            output = function(*args, **kwargs)
            b=_function_output_string.format(function.__name__, str_args, output)
            _print_function(_function_output_string.format(function.__name__, str_args, output))
            return output
        return function(*args, **kwargs)  # output
    return wrapper

