from unittest.mock import Mock
from llobot.commands.knowledge import LoadKnowledgeCommand
from llobot.environments import Environment
from llobot.environments.cutoffs import CutoffEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.archives import KnowledgeArchive
from llobot.projects import Project
from llobot.time import current_time

def test_load_knowledge_command():
    archive = Mock(spec=KnowledgeArchive)
    command = LoadKnowledgeCommand(archive)
    env = Environment()

    mock_knowledge = Knowledge({'a.txt': 'hello'})
    archive.last.return_value = mock_knowledge
    project = Mock(spec=Project)
    project.name = "test-project"

    cutoff = current_time()

    env[ProjectEnv].set(project)
    env[CutoffEnv].set(cutoff)

    command.process(env)

    archive.last.assert_called_once_with(project.name, cutoff)
    assert env[KnowledgeEnv].get() == mock_knowledge

def test_load_knowledge_command_no_project():
    archive = Mock(spec=KnowledgeArchive)
    command = LoadKnowledgeCommand(archive)
    env = Environment()
    knowledge_env = env[KnowledgeEnv]

    command.process(env)

    archive.last.assert_not_called()
    assert knowledge_env.get() == Knowledge() # empty

def test_load_knowledge_command_no_cutoff():
    archive = Mock(spec=KnowledgeArchive)
    command = LoadKnowledgeCommand(archive)
    env = Environment()
    knowledge_env = env[KnowledgeEnv]

    mock_knowledge = Knowledge({'a.txt': 'hello'})
    archive.last.return_value = mock_knowledge
    project = Mock(spec=Project)
    project.name = "test-project"

    env[ProjectEnv].set(project)
    # No cutoff set

    command.process(env)

    archive.last.assert_called_once_with(project.name, None)
    assert env[KnowledgeEnv].get() == mock_knowledge
