import logging
import re
import string


def handle_percent_format(format_string: str, *args, **kwargs) -> str:
    """
    Format a string using percent-style formatting. Only standard format specifiers (diouxXeEfFgGcrs%) are allowed for safety

    The function performs the following safety measures:
    1. Escapes literal percent signs (%)
    2. Validates that format specifiers are safe (limited to standard types)
    3. Catches and logs formatting errors rather than raising exceptions
    4. Properly restores literal percent signs after formatting

    Args:
        format_string (str): The string containing percent-style format specifiers
        *args: Positional arguments to be used for positional percent formatting
        **kwargs: Keyword arguments to be used for named parameter percent formatting

    Returns:
        str: The formatted string after all substitutions are applied

    Examples:
        >>> handle_percent_format("Hello, %s!", "world")
        'Hello, world!'
        >>> handle_percent_format("%(name)s is %(age)d years old", name="Alice", age=30)
        'Alice is 30 years old'
    """
    # First, escape any literal percent signs that aren't part of format specifiers
    processed_format = format_string
    
    # Handle percent-style formatting with comprehensive validation
    if '%' in format_string:
        # Check for literal percent signs (escaped as %%)
        processed_format = re.sub(r'%%', lambda _: '\\%', processed_format)
        
        # Handle positional percent formatting with comprehensive validation
        positional_pattern = r'%(?:[-+0# ]*(?:\d+|\*)?(?:\.(?:\d+|\*))?[diouxXeEfFgGcrs%])'
        if args and re.search(positional_pattern, processed_format):
            try:
                # Validate the format string contains only safe format specifiers
                if all(specifier in 'diouxXeEfFgGcrs%' for specifier in 
                       [m[-1] for m in re.findall(r'%(?:[-+0# ]*(?:\d+|\*)?(?:\.(?:\d+|\*))?([diouxXeEfFgGcrs%]))', processed_format)]):
                    # Apply formatting
                    processed_format = processed_format % args
                else:
                    logging.warning("Potentially unsafe format specifiers detected in positional formatting")
            except (TypeError, ValueError) as e:
                logging.warning(f"Error during positional percent formatting: {e}")
        
        # Handle named parameter formatting with comprehensive validation
        named_pattern = r'%\([^)]+\)(?:[-+0# ]*(?:\d+|\*)?(?:\.(?:\d+|\*))?[diouxXeEfFgGcrs])'
        if kwargs and re.search(named_pattern, processed_format):
            try:
                # Extract all format specifiers to validate them
                safe_pattern = r'%\(([^)]+)\)(?:[-+0# ]*(?:\d+|\*)?(?:\.(?:\d+|\*))?([diouxXeEfFgGcrs]))'
                if all(specifier in 'diouxXeEfFgGcrs' for _, specifier in re.findall(safe_pattern, processed_format)):
                    # Apply formatting
                    processed_format = processed_format % kwargs
                else:
                    logging.warning("Potentially unsafe format specifiers detected in named parameter formatting")
            except (TypeError, ValueError, KeyError) as e:
                logging.warning(f"Error during named parameter percent formatting: {e}")

        # Restore literal percent signs
        processed_format = processed_format.replace('\\%', '%')
        return processed_format


class SafeFormatter(string.Formatter):
    """
    A custom string formatter that safely handles missing keys and invalid format strings.
    
    This class extends the built-in string.Formatter to provide more robust formatting
    capabilities, particularly when dealing with potentially missing keys or malformed
    format strings.
    """

    def get_value(self, key, args, kwargs):
        """
        Retrieve a value for a given key from kwargs, or return a placeholder if not found.
        Args:
            key: The key to look up in kwargs.
            args: Positional arguments (not used in this implementation).
            kwargs: Keyword arguments containing the values to format.

        Returns:
            The value associated with the key if found in kwargs, otherwise a placeholder
            string containing the key.
        """
        if isinstance(key, str):
            return kwargs.get(key, "{" + key + "}")
        else:
            return super().get_value(key, args, kwargs)

    def parse(self, format_string):
        """
        Parse the format string, handling potential ValueError exceptions.

        Args:
            format_string: The string to be parsed for formatting.

        Returns:
            A list of tuples representing the parsed format string. If parsing fails,
            returns a list with a single tuple containing the entire format string.
        """
        try:
            return super().parse(format_string)
        except ValueError:
            return [(format_string, None, None, None)]


def safe_format(format_string: str, *args, **kwargs) -> str:
    """
    Format a string safely, handling both brace-style ({}) and percent-style (%) formatting.
    
    Example:
    >>> kwargs = {
    >>>     "first": 1,
    >>>     "second": "second",
    >>>     "third": get_bool("three"),
    >>>     "fourth": 2*2
    >>> }
    >>> with open("text.txt", "r") as file:
    >>>     string = file.read()
    >>> return string
    "{first}, {second}, {third}, {fourth}, fifth"
    >>> string = safe_format(string, **kwargs)
    >>> return string
    "1, second, True, 4, fifth"

    Args:
        format_string: The string to be formatted.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments to be used in formatting.

    Returns:
        A formatted string where keys from kwargs are substituted into the format_string.
        Missing keys are left as is in the resulting string.
    """
    # if '%' in format_string:
    #     return handle_percent_format(format_string, *args, **kwargs)

    formatter = SafeFormatter()
    return formatter.format(format_string, *args, **kwargs)
