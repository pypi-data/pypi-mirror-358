import sys
import typing as t
from dataclasses import dataclass
from pathlib import Path
from subprocess import PIPE, Popen
from typing import Optional

import sleazy


# find sass binary:
def sass_binary() -> Path:
    src = Path(__file__).parent
    return src / "vendor" / "dart-sass" / "sass"


SASS = sass_binary()


class SassquatchError(Exception):
    """
    General exception for Sassquatch-related errors.

    This class serves as a base exception for any errors specifically related
    to the Sassquatch framework or its components. It can be used to handle
    custom errors related to Sassquatch, differentiate them from other exceptions,
    and provide more specific error messages or debugging information.
    """


class InvalidCompileOption(SassquatchError):
    """
    Represents an error raised when an invalid compilation option is encountered.
    """


@dataclass
class CompileError(SassquatchError):
    """
    Represents an error thrown by dart-sass.
    """

    exit_code: int = 1
    stdout: str = ""
    stderr: str = ""

    def __str__(self):
        return f"\n[exit code]\n{self.exit_code}\n\n[stdout]\n{self.stdout}\n\n[stderr]\n{self.stderr}\n\n"


T = t.TypeVar("T")


class SassSettings(t.TypedDict, total=False):
    # sassquatch
    filename: t.Annotated[str, "?"]  # optional for stdin
    version: bool
    sass_update: bool
    # dart-sass (https://sass-lang.com/documentation/cli/dart-sass/)
    indented: bool
    load_path: list[str]
    pkg_importer: str
    style: t.Literal["expanded", "compressed"]
    no_charset: bool
    error_css: bool
    # these options only work on directories:
    update: bool
    no_source_map: bool
    source_map_urls: t.Literal["relative", "absolute"]
    embed_sources: bool
    embed_source_map: bool
    watch: bool
    verbose: bool
    quiet: bool


def choose_exactly_n(options: t.Iterable[T], n: int = 1) -> bool:
    """
    Determines if exactly `n` unique, non-None elements exist in the provided options.

    This function ensures that the given `options` contain precisely `n` unique
    elements that are not `None`. If the `options` are not a set, they are
    converted into one.

    Args:
        options: A collection of elements to evaluate for uniqueness and count.
        n: The exact number of unique non-None elements to check against.

    Returns:
        True if exactly `n` unique, non-None elements exist in `options`,
        otherwise False.
    """
    options = set(options) if not isinstance(options, set) else options

    return len(options - {None}) == n


def run(args: list[Path | str], stdin: str = "", quiet: bool = False):
    """
    Executes a subprocess with the given command-line arguments.

    Provides functionality to
    capture standard input, standard output, and standard error. Allows raising exceptions
    for non-zero exit codes and suppressing error output.

    Args:
        args (list[Path | str]): A list of command-line arguments passed to the subprocess.
        stdin (str, optional): A string to pass as standard input to the subprocess.
            Defaults to an empty string.
        quiet (bool, optional): If True, suppresses printing standard error to the console.
            Defaults to False.

    Raises:
        CompileError: Raised when the subprocess exits with a non-zero exit code. The exception
            includes the exit code, standard output, and standard error.

    Returns:
        str: The standard output produced by the subprocess.
    """
    p = Popen(args, stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
    stdout, stderr = p.communicate(input=stdin)
    exit_code = p.returncode

    if exit_code > 0:
        raise CompileError(
            exit_code,
            stdout,
            stderr,
        )

    if not quiet:
        print(stderr, file=sys.stderr)

    return stdout


def compile_string(
    string: str, sass: Path = SASS, **settings: t.Unpack[SassSettings]
) -> str:
    """
    Compiles SCSS code from a string.

    Args:
        string: input scss string
        sass: Path to dart-sass binary/script

    Returns:
        string: output css string

    Raises:
        CompilationError: when something goes wrong in dart-sass
    """

    kwargs = sleazy.stringify(settings, SassSettings)

    return run([sass, "-"] + kwargs, stdin=string, quiet=settings.get("quiet", False))


def compile_path(path: Path, sass: Path = SASS, **settings: t.Unpack[SassSettings]):
    """
    Compiles a given Sass file into CSS using the specified settings.

    The function accepts a path to a Sass file and optional settings to
    customize the compilation process. It formats the provided settings,
    executes the Sass compiler, and returns the result.

    Args:
        path (Path): The path to the Sass file to be compiled.
        sass (Path): Optional. The path to the Sass compiler executable.
            Defaults to the SASS constant.
        settings (**SassSettings): Additional settings for the Sass
            compiler provided as keyword arguments.

    Returns:
        Any: The result of the Sass compilation process.

    Raises:
        None
    """
    kwargs = sleazy.stringify(settings, SassSettings)

    return run([sass, path] + kwargs, quiet=settings.get("quiet", False))


def compile(
    string: Optional[str] = None,
    path: Optional[str | Path] = None,
    **settings: t.Unpack[SassSettings],
) -> str:
    """
    Compiles SCSS code from either a string, file or directory (exactly one of these options must be chosen).

    Raises:
        InvalidCompileOption: when invalid options are passed
        CompilationError: when something goes wrong in dart-sass
    """
    if not choose_exactly_n({string, path}, 1):
        raise InvalidCompileOption("Exactly one of string or path must be provided.")

    if string is not None:
        return compile_string(string, **settings)
    elif path is not None:
        filepath = Path(path) if not isinstance(path, Path) else path
        # todo: don't read file (so more features like --watch work); support directories
        return compile_path(filepath, **settings)
    else:
        # this should already be checked by `choose_exactly_n` but let's just throw the error again anyway:
        raise InvalidCompileOption("Exactly one of string or path must be provided.")


def show_versions(sass: Path = SASS) -> None:
    from .__about__ import __version__ as sassquatch_version

    dart_sass_version = run([sass, "--version"])

    print("Sassquatch:", sassquatch_version)
    print("Dart Sass: ", dart_sass_version)


def sass_update():
    """
    Update the vendor version of dart-sass.

    This function facilitates updating the dart-sass vendor version by utilizing
    the `install_dart_sass` function from the build module and specifying the
    appropriate package directory.

    Raises:
        Any exceptions raised by the `install_dart_sass` function.

    """
    from .build import install_dart_sass  # noqa

    pkg_dir = Path(__file__).parent
    install_dart_sass(pkg_dir)


def main() -> None:
    """
    Processes SCSS input and outputs a corresponding response.

    This function takes SCSS code either from a file/files/directory specified
    via command-line arguments or from standard input. It then processes the
    SCSS code and provides an appropriate output or result.
    """
    # use sys.argv to compile file/files/directory or otherwise use stdin
    settings = sleazy.parse(SassSettings)

    if settings.get("sass_update"):
        return sass_update()

    if not SASS.exists():
        print(
            "ERR: missing sass binary, the program can not continue.", file=sys.stderr
        )
        print(
            "Try `sassquatch --sass-update` to download the dependency.",
            file=sys.stderr,
        )
        exit(1)

    if settings.get("version"):
        return show_versions()

    try:
        if (filename := settings.pop("filename", None)) and filename != "-":
            result = compile(path=filename, **settings)
        else:
            print("No filename passed, reading from stdin:\n", file=sys.stderr)
            string = sys.stdin.read()  # until end of input
            result = compile(string, **settings)
    except CompileError as e:
        print(e, file=sys.stderr)
        exit(e.exit_code)

    if result.strip():
        print("--- start of compiled css ---", file=sys.stderr)
        print(result)

    exit(0)
