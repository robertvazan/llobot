from pathlib import Path
from unittest.mock import Mock
from llobot.commands.knowledge import ProjectKnowledgeStep
from llobot.environments import Environment
from llobot.environments.cutoff import CutoffEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.archives import KnowledgeArchive
from llobot.projects.directory import DirectoryProject
from llobot.utils.time import current_time

def test_project_knowledge_step(tmp_path: Path):
    archive = Mock(spec=KnowledgeArchive)
    step = ProjectKnowledgeStep(archive)
    env = Environment()

    k1 = Knowledge({'a.txt': 'hello'})
    k2 = Knowledge({'b.txt': 'world'})
    p1_prefix = Path('p1')
    p2_prefix = Path('p2')

    p1 = DirectoryProject(tmp_path / 'p1', prefix=p1_prefix)
    p2 = DirectoryProject(tmp_path / 'p2', prefix=p2_prefix)

    cutoff = current_time()
    archive.last.side_effect = lambda zone, c: k1 if zone == p1_prefix else (k2 if zone == p2_prefix else Knowledge())

    env[ProjectEnv].add(p1)
    env[ProjectEnv].add(p2)
    env[CutoffEnv].set(cutoff)

    step.process(env)

    archive.last.assert_any_call(p1_prefix, cutoff)
    archive.last.assert_any_call(p2_prefix, cutoff)
    expected_knowledge = (p1_prefix / k1) | (p2_prefix / k2)
    assert env[KnowledgeEnv].get() == expected_knowledge

def test_project_knowledge_step_no_project():
    archive = Mock(spec=KnowledgeArchive)
    step = ProjectKnowledgeStep(archive)
    env = Environment()
    knowledge_env = env[KnowledgeEnv]

    step.process(env)

    archive.last.assert_not_called()
    assert knowledge_env.get() == Knowledge() # empty

def test_project_knowledge_step_no_cutoff(tmp_path: Path):
    archive = Mock(spec=KnowledgeArchive)
    step = ProjectKnowledgeStep(archive)
    env = Environment()

    mock_knowledge = Knowledge({'a.txt': 'hello'})
    prefix = Path('test-project')
    project = DirectoryProject(tmp_path / prefix, prefix=prefix)

    archive.last.return_value = mock_knowledge

    env[ProjectEnv].add(project)
    # No cutoff set

    step.process(env)

    archive.last.assert_called_once_with(prefix, None)
    assert env[KnowledgeEnv].get() == (prefix / mock_knowledge)
