from pathlib import Path
from unittest.mock import patch, Mock

from llobot.commands.knowledge import ProjectKnowledgeStep
from llobot.environments import Environment
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.knowledge import Knowledge
from llobot.projects.directory import DirectoryProject
from llobot.projects.library import ProjectLibrary
from llobot.projects.union import union_project


def test_project_knowledge_step(tmp_path: Path):
    step = ProjectKnowledgeStep()
    env = Environment()

    p1_prefix = Path('p1')
    p1_path = tmp_path / 'p1'
    p1_path.mkdir()
    (p1_path / 'a.txt').write_text('hello')
    p1 = DirectoryProject(p1_path, prefix=p1_prefix)

    p2_prefix = Path('p2')
    p2_path = tmp_path / 'p2'
    p2_path.mkdir()
    (p2_path / 'b.txt').write_text('world')
    p2 = DirectoryProject(p2_path, prefix=p2_prefix)

    library = Mock(spec=ProjectLibrary)
    library.lookup.side_effect = lambda key: {'p1': [p1], 'p2': [p2]}.get(key, [])
    project_env = env[ProjectEnv]
    project_env.configure(library)
    project_env.add('p1')
    project_env.add('p2')

    step.process(env)

    expected_knowledge = Knowledge({
        Path('p1/a.txt'): 'hello\n',
        Path('p2/b.txt'): 'world\n',
    })
    assert env[KnowledgeEnv].get() == expected_knowledge


def test_project_knowledge_step_no_project():
    step = ProjectKnowledgeStep()
    env = Environment()
    knowledge_env = env[KnowledgeEnv]

    step.process(env)

    assert knowledge_env.get() == Knowledge()  # empty
