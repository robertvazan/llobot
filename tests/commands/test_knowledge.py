from pathlib import Path
from unittest.mock import Mock
from llobot.commands.knowledge import ProjectKnowledgeStep
from llobot.environments import Environment
from llobot.environments.cutoff import CutoffEnv
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

    k1 = Knowledge({Path('p1/a.txt'): 'hello'})
    k2 = Knowledge({Path('p2/b.txt'): 'world'})

    p1 = Mock(spec=Project)
    p1.name = "p1"
    p1.last.return_value = k1
    p2 = Mock(spec=Project)
    p2.name = "p2"
    p2.last.return_value = k2

    cutoff = current_time()

    env[ProjectEnv].add(p1)
    env[ProjectEnv].add(p2)
    env[CutoffEnv].set(cutoff)

    step.process(env)

    p1.last.assert_called_once_with(archive, cutoff)
    p2.last.assert_called_once_with(archive, cutoff)
    expected_knowledge = k1 | k2
    assert env[KnowledgeEnv].get() == expected_knowledge

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

    mock_knowledge = Knowledge({Path('test-project/a.txt'): 'hello'})
    project = Mock(spec=Project)
    project.name = "test-project"
    project.last.return_value = mock_knowledge

    env[ProjectEnv].add(project)
    # No cutoff set

    step.process(env)

    project.last.assert_called_once_with(archive, None)
    assert env[KnowledgeEnv].get() == mock_knowledge
