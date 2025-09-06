from unittest.mock import Mock
from llobot.commands.knowledge import LoadKnowledgeCommand
from llobot.environments import Environment
from llobot.environments.cutoffs import CutoffEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.knowledge import Knowledge
from llobot.projects import Project
from llobot.time import current_time

def test_load_knowledge_command():
    command = LoadKnowledgeCommand()
    env = Environment()

    mock_knowledge = Knowledge({'a.txt': 'hello'})
    project = Mock(spec=Project)
    project.knowledge.return_value = mock_knowledge

    cutoff = current_time()

    env[ProjectEnv].set(project)
    env[CutoffEnv].set(cutoff)

    command.process(env)

    project.knowledge.assert_called_once_with(cutoff)
    assert env[KnowledgeEnv].get() == mock_knowledge

def test_load_knowledge_command_no_project():
    command = LoadKnowledgeCommand()
    env = Environment()
    knowledge_env = env[KnowledgeEnv]

    command.process(env)

    assert knowledge_env.get() == Knowledge() # empty

def test_load_knowledge_command_no_cutoff():
    command = LoadKnowledgeCommand()
    env = Environment()
    knowledge_env = env[KnowledgeEnv]

    mock_knowledge = Knowledge({'a.txt': 'hello'})
    project = Mock(spec=Project)
    project.knowledge.return_value = mock_knowledge

    env[ProjectEnv].set(project)
    # No cutoff set

    command.process(env)

    project.knowledge.assert_called_once_with(None)
    assert env[KnowledgeEnv].get() == mock_knowledge
