from llobot.commands.autonomy import handle_autonomy_commands
from llobot.environments import Environment
from llobot.environments.commands import CommandsEnv
from llobot.environments.autonomy import AutonomyEnv
from llobot.roles.autonomy import Autonomy, NoAutonomy, StepAutonomy

default_autonomy = NoAutonomy()
step_autonomy = StepAutonomy()
profiles = {'step': step_autonomy}

def test_handle_autonomy_command():
    env = Environment()
    env[AutonomyEnv].configure(default_autonomy, profiles)
    env[CommandsEnv].add('autonomy:step')

    handle_autonomy_commands(env)

    assert env[AutonomyEnv].get() == step_autonomy
    assert not env[CommandsEnv].get()

def test_handle_autonomy_command_not_found():
    env = Environment()
    env[AutonomyEnv].configure(default_autonomy, profiles)
    env[CommandsEnv].add('autonomy:unknown')

    handle_autonomy_commands(env)

    # Should remain default
    assert env[AutonomyEnv].get() == default_autonomy
    # Command was not consumed because handle_autonomy_command returns False for unfound profile
    assert env[CommandsEnv].get() == ['autonomy:unknown']

def test_handle_invalid_command_format():
    env = Environment()
    env[AutonomyEnv].configure(default_autonomy, profiles)
    env[CommandsEnv].add('autonomy') # Missing colon and profile name

    handle_autonomy_commands(env)

    assert env[AutonomyEnv].get() == default_autonomy
    assert env[CommandsEnv].get() == ['autonomy']
