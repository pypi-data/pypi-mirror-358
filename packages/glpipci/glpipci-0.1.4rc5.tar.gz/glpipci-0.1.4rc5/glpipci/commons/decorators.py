import os
from functools import wraps
from dotenv import load_dotenv


def debug_print_params(func):
    """
    Decorator to print function parameters if DEBUG environment variable is '1' or 'true'.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        load_dotenv()
        debug_env = os.environ.get('DEBUG', '0').lower()
        if debug_env in ('1', 'true'):
            print(f"Calling function: {func.__name__}")
            print(f"  Args: {args}")
            print(f"  Kwargs: {kwargs}")
        return func(*args, **kwargs)
    return wrapper
