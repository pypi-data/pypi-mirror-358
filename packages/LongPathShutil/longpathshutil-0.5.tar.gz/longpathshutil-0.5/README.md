
# LongPathShutil

**LongPathShutil** is a drop-in Python wrapper for the methods of the built-in `shutil` library, providing enhanced support for long file paths on Windows. It leverages the `\\?\` prefix to bypass the 260-character path length limit on Windows systems, and to be able to handle deeply nested or long file names. More info on the long path limitations on windows [here](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=registry)

## Features

- Seamlessly integrates long path support on Windows.
- Fully compatible with the existing `shutil` functions. The functions only.
- Automatically prefixes paths with `\\?\` when necessary.
- Offers functions to enable or disable long path support via the Windows registry
  at least for the applications supporting it. (Needs to be executed as admin)

## Installation

You can install it like so:

```bash
pip install LongPathShutil
```

## Usage

### Enabling Long Paths in the Windows Registry

You can try programmatically enabling long paths via the registry.
This does however require admin access and does not always work.
Otherwise you can use the module as drop-in replacement for shutil on windows.

```python
import LongPathShutil

# Enable long paths in the Windows registry (requires administrative privileges)
LongPathShutil.enable_long_paths_on_registry()
```

### Basic File Operations

```python
import LongPathShutil as shutil

# Copy a file with long paths
shutil.copy(r"C:\very\long\source\path\file.txt", r"C:\another\very\long\destination\path\file.txt")

# Move a directory with long paths
shutil.move(r"C:\very\long\source\directory", r"C:\another\very\long\destination\directory")

# Remove a directory tree with long paths
shutil.rmtree(r"C:\very\long\path\to\directory")
```

### Full API

The `LongPathShutil` class provides all the functions available in `shutil` with the addition of long path support:

- `copyfile()`, `copy()`, `copy2()`
- `move()`, `rmtree()`, `copytree()`
- `make_archive()`, `unpack_archive()`, `get_archive_formats()`, and more.

See the complete list of functions [here](https://docs.python.org/3/library/shutil.html).

## Why Use LongPathShutil?

By default, Windows imposes a 260-character limit on paths, which can cause problems when dealing with deeply nested directory structures or long filenames. This module automatically adds the necessary prefix to bypass this limitation, allowing for seamless file operations across various platforms.

## Contributing

If you find a bug or have a suggestion, feel free to open an issue or submit a pull request. Make sure to check the `CONTRIBUTING.md` for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
