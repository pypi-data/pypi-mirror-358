"""
Status: Testing
"""
import os
from dataclasses import dataclass
from typing import Optional, Any, TypeVar, Type, Callable, Generic

__all__ = ['RequiredEnvironmentVariable', 'required_env', 'optional_env', 'required_flag', 'optional_flag', 'flag']

T = TypeVar('T')
ValueConverter = Callable[[Optional[str]], T]


@dataclass
class EnvironmentVariable(Generic[T]):
    name: str
    variable_type: str
    interpretation_type: Type[T]
    required: bool
    help: Optional[str]


class RequiredEnvironmentVariable(RuntimeError):
    def __init__(self, env, help):
        super().__init__(env, help)

    def __repr__(self):
        return f'{self.args[0]}: {self.args[1]}'


class EnvironmentVariableManager:
    """ Manage environment variables. """

    def __init__(self):
        self._variables: dict[str, EnvironmentVariable] = dict()

    def _parse_value(self, raw_value: Optional[str], kind: Type[T]) -> T:
        if raw_value is None:
            return None
        return kind(raw_value)

    def required_env(self, env: str,
                     *,
                     kind: Type[T] = str,
                     convert: Optional[ValueConverter] = None,
                     help: Optional[str] = None,
                     variable_type='variable') -> T:
        """ Get the required environment variable.

            When the environment variable is undefined, this function will raise an exception.
        """
        if env not in self._variables:
            self._variables[env] = EnvironmentVariable(
                name=env,
                variable_type=variable_type,
                interpretation_type=kind,
                required=True,
                help=help,
            )

        if env not in os.environ:
            raise RequiredEnvironmentVariable(env, help or "Your need to set this environment variable.")

        return self._parse_value(os.environ[env], convert or kind)

    def optional_env(self, env: str,
                     default: Any = None,
                     *,
                     kind: Type[T] = str,
                     convert: Optional[ValueConverter] = None,
                     help: Optional[str] = None,
                     variable_type='variable') -> T:
        """ Get the optional environment variable.

            When the environment variable is undefined, this function will return the default value.
        """
        if env not in self._variables:
            self._variables[env] = EnvironmentVariable(
                name=env,
                variable_type=variable_type,
                interpretation_type=kind,
                required=True,
                help=help,
            )

        read_value = os.getenv(env, default)
        return self._parse_value(read_value, convert or kind) if read_value is not None else None

    def _parse_bool_value(self, raw_value: Optional[str]) -> T:
        if raw_value is None:
            return None
        elif raw_value.lower().strip() in ('1', 'true', 'yes'):
            return True
        elif raw_value.lower().strip() in ('0', 'false', 'no'):
            return False
        else:
            raise ValueError(f'"{raw_value}" is not a interpretable boolean value.')

    def required_flag(self, env: str, *, help: Optional[str] = None) -> bool:
        """ Check if the flag is set via environment variable.

            The behaviour of this method is the similar to required_env.

            If the non-boolean value is given, it will raise an exception.
        """
        return self.required_env(env, convert=self._parse_bool_value, help=help, variable_type='flag')

    def optional_flag(self, env: str, *, help: Optional[str] = None) -> bool:
        """ Check if the flag is set via environment variable.

            The behaviour of this method is the similar to required_env.

            If the non-boolean value is given, it will raise an exception.
        """
        return self.optional_env(env, convert=self._parse_bool_value, help=help, variable_type='flag') or False

    flag = optional_flag


manager = EnvironmentVariableManager()
required_env = manager.required_env
optional_env = manager.optional_env
required_flag = manager.required_flag
optional_flag = manager.optional_flag
flag = manager.flag
