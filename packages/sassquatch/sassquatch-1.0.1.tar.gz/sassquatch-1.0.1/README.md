# Sassquatch

Sassquatch is a Python wrapper for [Dart Sass](https://sass-lang.com/dart-sass/), providing a convenient way to compile
Sass/SCSS to CSS in your Python applications.

[![PyPI version](https://img.shields.io/pypi/v/sassquatch.svg)](https://pypi.org/project/sassquatch/)

## Installation

Install Sassquatch with your package manager of choice:

```bash
uv add sassquatch
# or, good old:
pip install sassquatch
```

During installation, Sassquatch will automatically download the latest version of Dart Sass for your platform.

## Features

- Compile Sass/SCSS from strings, files, or directories
- Full compatibility with Dart Sass's compilation features
- Use as a command-line tool or as a Python library
- Automatic download and management of the Dart Sass binary

## Usage

### Command Line Interface

Sassquatch follows [Dart Sass CLI semantics](https://sass-lang.com/documentation/cli/dart-sass/):

```bash
# Compile a file to stdout
sassquatch path/to/input.scss

# Compile a file to a specific output file
sassquatch path/to/input.scss:path/to/output.css

# Compile a directory
sassquatch path/to/input_dir:path/to/output_dir

# Compile from stdin
echo "body { color: red; }" | sassquatch

# Compile with options
sassquatch path/to/input.scss --style=compressed --no-charset

# update embedded sass version:
sassquatch --sass-update

# see all options:
sassquatch --help
```

### Python API

```python
from sassquatch import compile

# Compile a string
css = compile(string='$primary: #333; body { color: $primary; }')

# Compile a file
css = compile(path='styles.scss')

# Compile with options
css = compile(
    path='styles.scss',
    style='compressed',
    no_charset=True,
    load_path=['node_modules']
)
```

## Configuration

Sassquatch supports all Dart Sass command-line options:

| Option               | Description                                                            |
|----------------------|------------------------------------------------------------------------|
| `--style`            | Output style: `expanded` or `compressed`                               |
| `--no-charset`       | Don't emit a `@charset` or BOM for CSS with non-ASCII characters       |
| `--error-css`        | When compilation fails, emit error messages as CSS                     |
| `--load-path`        | Path to look for imported files                                        |
| `--no-source-map`    | Disable source map generation                                          |
| `--source-map-urls`  | How to link from source maps to source files: `relative` or `absolute` |
| `--embed-sources`    | Embed source file contents in source maps                              |
| `--embed-source-map` | Embed source map contents in CSS                                       |
| `--watch`            | Watch for changes and recompile as needed                              |
| `--update`           | Only compile out-of-date files                                         |
| `--verbose`          | Print more information                                                 |
| `--quiet`            | Don't print warnings                                                   |

For a full list of options, refer to the [Dart Sass documentation](https://sass-lang.com/documentation/cli/dart-sass/).

## Implementation Details

Sassquatch is based on Dart Sass (embedded mode) and downloads the latest version of the Dart Sass binary during
installation. This ensures you always have access to the most up-to-date Sass features and fixes.

## License

This project is licensed under the MIT License.

## Acknowledgments

- [Dart Sass](https://sass-lang.com/dart-sass/) - The core Sass compiler