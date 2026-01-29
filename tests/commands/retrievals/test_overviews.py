from pathlib import PurePosixPath, Path
from llobot.commands.retrievals.overviews import assume_overview_retrieval_commands
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.subsets.parsing import parse_pattern
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.predefined import PredefinedProjectLibrary

OVERVIEWS = parse_pattern('README.md', '__init__.py')
KNOWLEDGE = {
    PurePosixPath('README.md'): 'root readme',
    PurePosixPath('a/__init__.py'): 'a init',
    PurePosixPath('a/README.md'): 'a readme',
    PurePosixPath('a/b/doc.txt'): 'not an overview',
    PurePosixPath('a/b/file.txt'): 'some file',
    PurePosixPath('a/b/__init__.py'): 'a/b init',
    PurePosixPath('c/file.txt'): 'another file'
}

def create_env(tmp_path: Path, files: dict[PurePosixPath, str]) -> Environment:
    env = Environment()
    root = tmp_path / 'project'
    root.mkdir()
    for path, content in files.items():
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

    project = DirectoryProject(root, prefix=PurePosixPath('project'))
    library = PredefinedProjectLibrary({'project': project})

    project_env = env[ProjectEnv]
    project_env.configure(library)
    project_env.add('project')

    return env

def test_no_retrievals(tmp_path):
    env = create_env(tmp_path, KNOWLEDGE)
    assume_overview_retrieval_commands(env, overviews=OVERVIEWS)
    assert not env[RetrievalsEnv].get()

def test_retrieval_in_subdir(tmp_path):
    env = create_env(tmp_path, KNOWLEDGE)
    env[RetrievalsEnv].add(PurePosixPath('project/a/b/file.txt'))
    assume_overview_retrieval_commands(env, overviews=OVERVIEWS)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([
        PurePosixPath('project/a/b/file.txt'),
        PurePosixPath('project/README.md'),
        PurePosixPath('project/a/__init__.py'),
        PurePosixPath('project/a/README.md'),
        PurePosixPath('project/a/b/__init__.py'),
    ])

def test_retrieval_in_root(tmp_path):
    knowledge = KNOWLEDGE.copy()
    knowledge[PurePosixPath('root.txt')] = 'i am root'
    env = create_env(tmp_path, knowledge)
    env[RetrievalsEnv].add(PurePosixPath('project/root.txt'))
    assume_overview_retrieval_commands(env, overviews=OVERVIEWS)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([
        PurePosixPath('project/root.txt'),
        PurePosixPath('project/README.md'),
    ])

def test_multiple_retrievals(tmp_path):
    env = create_env(tmp_path, KNOWLEDGE)
    env[RetrievalsEnv].add(PurePosixPath('project/a/b/file.txt'))
    env[RetrievalsEnv].add(PurePosixPath('project/c/file.txt'))
    assume_overview_retrieval_commands(env, overviews=OVERVIEWS)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([
        PurePosixPath('project/a/b/file.txt'),
        PurePosixPath('project/c/file.txt'),
        PurePosixPath('project/README.md'),
        PurePosixPath('project/a/__init__.py'),
        PurePosixPath('project/a/README.md'),
        PurePosixPath('project/a/b/__init__.py'),
    ])

def test_retrieved_is_overview(tmp_path):
    env = create_env(tmp_path, KNOWLEDGE)
    env[RetrievalsEnv].add(PurePosixPath('project/a/README.md'))
    assume_overview_retrieval_commands(env, overviews=OVERVIEWS)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([
        PurePosixPath('project/a/README.md'),
        PurePosixPath('project/README.md'),
        PurePosixPath('project/a/__init__.py'),
    ])
