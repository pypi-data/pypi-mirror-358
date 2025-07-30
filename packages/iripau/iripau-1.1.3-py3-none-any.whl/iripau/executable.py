"""
Execute commands as Python functions
"""

from shlex import split
from random import choice
from itertools import chain

from iripau.command import host_run


class Command:
    """ Run an executable command as a Python callable



    """

    def __init__(self, parent, command):
        self._parent = parent
        self._command = parent._mk_command(command)
        self._mk_command = parent._mk_command

    def __getattr__(self, command):
        child = Command(self, command)
        setattr(self, command, child)
        return child

    def __call__(self, *args, **kwargs):
        return self._parent(self._command, *args, **kwargs)


def make_command(command):
    """ Replace underscore with dash.

        Suitable for a CLI that uses dashes as word-separator in their
        positional arguments.

        Args:
            command (str): Python identifier referring to a CLI command or
                sub-command.

        Returns:
            str: Final token to be used as a CLI positional argument.
    """
    return command.replace("_", "-")


def make_option(option):
    """ Replace underscore with dash and prepend two more dashes.

        Suitable for a CLI that uses dashes as word-separator in their
        positional arguments.

        Args:
            option (str): Python identifier referring to a CLI optional
                argument.

        Returns:
            Tuple[str]: The tokens that could be used as a CLI positional argument.
    """
    return "--" + option.replace("_", "-"),


class Executable:
    """ Run an executable as a Python callable.

        Args:
            executable (str): Path to an executable file or just the name if it
                exists in the ``PATH``.
            make_command (Callable[[str], str]): Function to convert a Python
                identifier to the corresponding command positional argument for
                the CLI.
            make_option (Callable[str], Tuple[str]): Function to convert a Python
                identifier into the corresponding optional argument for the CLI.
                randomly, and
            alias (str, list(str)): Alias for ``executable``. See ``alias`` in
                `iripau.subprocess.Popen`_.
            run_args_prefix (str): When calling an instance of this class, all
                of the ``**kwargs`` starting with this prefix will be passed to
                the ``run_function`` after removing the prefix.
            run_function (Callable[List[str] *Any], subprocess.CompletedProcess):
                The function that will actually run the process, wait for it and
                return a ``CompletedProcess``.

                If ``None``, the default function is `iripau.command.host_run`_.
            **kwargs: Keyword arguments to be passed to ``run_function`` every
                time an instance of this object is called.
                The ``run_args_prefix`` is not needed here.
    """
    def __init__(
        self, executable, make_command=make_command, make_option=make_option,
        alias=None, run_args_prefix="_", run_function=None, **kwargs
    ):
        self._run = run_function or host_run
        self._exe = split(executable) if isinstance(executable, str) else executable
        self._alias = split(alias) if isinstance(alias, str) else alias
        self._kwargs = kwargs

        self._prefix = run_args_prefix
        self._mk_option = make_option
        self._mk_command = make_command

    def __getattr__(self, command):
        child = Command(self, command)
        setattr(self, command, child)
        return child

    def __call__(self, *args, **kwargs):
        optionals = chain.from_iterable(
            self._make_arg(self._mk_option(key), value)
            for key, value in kwargs.items()
            if not key.startswith(self._prefix)
        )

        positionals = list(map(str, args))
        optionals = list(optionals)

        kwargs = {
            key[len(self._prefix):]: value
            for key, value in kwargs.items()
            if key.startswith(self._prefix)
        }

        if self._alias:
            kwargs.setdefault("alias", self._alias + positionals + optionals)

        cmd = self._exe + positionals + optionals
        return self._run(cmd, **self._kwargs, **kwargs)

    @staticmethod
    def _is_iterable(value):
        if isinstance(value, (str, bytes)):
            return False
        return hasattr(value, "__iter__")

    @classmethod
    def _make_arg(cls, options, value):
        """ Return a list of tokens.

            Args:
                options (Tuple[str]): One of this strings will be randomly chosen.

                    If the chosen option starts with ``--``, there will be a
                    single token with the option and the value: ``["--option=value"]``

                    If not, there will be two tokens: ``["-o", "value"]``.
                value: The value of the optional argument for the CLI.

                    If ``True``, the option will be treated as a flag, with no
                    value: ``["--option"]``.

                    If ``False`` or ``None``, the option will be ignored: ``[]``.

                    If an iterable and not a string, the option will be repeated
                    for each item: ``["--option=value1", "--option=value2"]

                    Otherwise, it will be converted to a string before using it.
        """
        if cls._is_iterable(value):
            return chain.from_iterable(
                cls._make_arg(options, item)
                for item in value
            )

        if value in {None, False}:
            return []

        option = choice(options)
        if value is True:
            return [option]

        value = str(value)
        if option.startswith("--"):
            return [option + "=" + value]
        return [option, value]
