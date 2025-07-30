"""
Simple hello world module for flex-evals package.
"""


def hello_world(name: str = "World") -> str:
    """
    Return a greeting message.
    
    Args:
        name: The name to greet. Defaults to "World".
        
    Returns:
        A greeting string.
        
    Example:
        >>> hello_world()
        'Hello, World!'
        >>> hello_world("Python")
        'Hello, Python!'
    """
    return f"Hello, {name}!"


def get_version() -> str:
    """
    Get the package version.
    
    Returns:
        The current package version.
    """
    from . import __version__
    return __version__