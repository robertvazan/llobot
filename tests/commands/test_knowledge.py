from unittest.mock import Mock
from llobot.commands.knowledge import ProjectKnowledgeStep
from llobot.environments import Environment
from llobot.environments.cutoffs import CutoffEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.archives import KnowledgeArchive
from llobot.projects import Project
from llobot.time import current_time

def test_project_knowledge_step():
    archive = Mock(spec=KnowledgeArchive)
    step = ProjectKnowledgeStep(archive)
    env = Environment()

    mock_knowledge = Knowledge({'a.txt': 'hello'})
    archive.last.return_value = mock_knowledge
    project = Mock(spec=Project)
    project.name = "test-project"

    cutoff = current_time()

    env[ProjectEnv].set(project)
    env[CutoffEnv].set(cutoff)

    step.process(env)

    archive.last.assert_called_once_with(project.name, cutoff)
    assert env[KnowledgeEnv].get() == mock_knowledge

def test_project_knowledge_step_no_project():
    archive = Mock(spec=KnowledgeArchive)
    step = ProjectKnowledgeStep(archive)
    env = Environment()
    knowledge_env = env[KnowledgeEnv]

    step.process(env)

    archive.last.assert_not_called()
    assert knowledge_env.get() == Knowledge() # empty

def test_project_knowledge_step_no_cutoff():
    archive = Mock(spec=KnowledgeArchive)
    step = ProjectKnowledgeStep(archive)
    env = Environment()
    knowledge_env = env[KnowledgeEnv]

    mock_knowledge = Knowledge({'a.txt': 'hello'})
    archive.last.return_value = mock_knowledge
    project = Mock(spec=Project)
    project.name = "test-project"

    env[ProjectEnv].set(project)
    # No cutoff set

    step.process(env)

    archive.last.assert_called_once_with(project.name, None)
    assert env[KnowledgeEnv].get() == mock_knowledge
