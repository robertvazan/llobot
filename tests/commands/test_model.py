from llobot.commands.model import handle_model_commands
from llobot.environments import Environment
from llobot.environments.commands import CommandsEnv
from llobot.environments.model import ModelEnv
from llobot.models.echo import EchoModel
from llobot.models.library.named import NamedModelLibrary

default_model = EchoModel('default')
m1 = EchoModel('m1')
library = NamedModelLibrary(m1)

def test_handle_model_command():
    env = Environment()
    env[ModelEnv].configure(library, default_model)
    env[CommandsEnv].add('m1')

    handle_model_commands(env)

    assert env[ModelEnv].get() == m1
    assert not env[CommandsEnv].get()

def test_handle_model_command_not_found():
    env = Environment()
    env[ModelEnv].configure(library, default_model)
    env[CommandsEnv].add('m2')

    handle_model_commands(env)

    assert env[ModelEnv].get() == default_model
    assert env[CommandsEnv].get() == ['m2']
