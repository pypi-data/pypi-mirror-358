
import inspect
import os
from pathlib import Path
import shutil
import sys
import winreg

def add_long_path_prefix(path):
    """
    Adds the \\?\ prefix to a path if it isn't already present.

    Args:
        path (Union[str, Path]): The path to add the prefix to.

    Returns:
        str: The path with the \\?\ prefix added, if applicable.
    """
    prefix = "\\\\?\\"
    unc_prefix = "\\\\?\\UNC\\"
    path = Path(path)

    if os.name == "nt":
        path_str = str(path)

        if not path.is_absolute():
            path = path.resolve()
            path_str = str(path)

        if path_str.startswith("\\\\"):
            if not path_str.startswith(unc_prefix):
                return unc_prefix + path_str[2:]
        else:
            if not path_str.startswith(prefix):
                return prefix + path_str

    return str(path)

# Parameters that need to be path-prefixed
PREFIX_KEYS = {"src", "dst", "path", "filename", "extract_dir"}

def auto_prefixer(func):
    try:
        sig = inspect.signature(func)
    except ValueError:
        # Can't get signature (e.g., built-in); skip
        return func

    def wrapper(*args, **kwargs):
        bound = sig.bind_partial(*args, **kwargs)
        bound.apply_defaults()

        for name in PREFIX_KEYS:
            if name in bound.arguments:
                value = bound.arguments[name]
                if isinstance(value, (str, Path)):
                    bound.arguments[name] = add_long_path_prefix(value)

        return func(*bound.args, **bound.kwargs)

    wrapper.__signature__ = sig
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__module__ = 'LongPathShutil'
    return wrapper

def wrap_shutil():
    wrapped_shutil = sys.modules[__name__]
    for name, obj in inspect.getmembers(shutil, inspect.isfunction):
        if obj.__module__ == "shutil":
            setattr(wrapped_shutil, name, auto_prefixer(obj))

# -------------------------------------------
# Windows registry helpers
# -------------------------------------------

def enable_long_paths_on_registry():
    key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        r"SYSTEM\\CurrentControlSet\\Control\\FileSystem",
        0,
        winreg.KEY_WRITE,
    )
    winreg.SetValueEx(key, "LongPathsEnabled", 0, winreg.REG_DWORD, 1)
    winreg.CloseKey(key)

def disable_long_paths_on_registry():
    key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        r"SYSTEM\\CurrentControlSet\\Control\\FileSystem",
        0,
        winreg.KEY_WRITE,
    )
    winreg.SetValueEx(key, "LongPathsEnabled", 0, winreg.REG_DWORD, 0)
    winreg.CloseKey(key)
    return True

def is_long_paths_enabled_on_registry():
    key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        r"SYSTEM\\CurrentControlSet\\Control\\FileSystem",
        0,
        winreg.KEY_READ,
    )
    value, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
    winreg.CloseKey(key)
    return value == 1

wrap_shutil()
