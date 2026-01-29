from pathlib import PurePosixPath, Path
from llobot.commands.retrievals.wildcard import handle_wildcard_retrieval_command
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.predefined import PredefinedProjectLibrary

KNOWLEDGE = {
    PurePosixPath('a/b.txt'): 'content',
    PurePosixPath('a/c.txt'): 'another',
    PurePosixPath('d.txt'): 'root file',
    PurePosixPath('x/y/z.txt'): 'deep file'
}

def create_env(tmp_path: Path) -> Environment:
    env = Environment()
    root = tmp_path / 'project'
    root.mkdir()
    for path, content in KNOWLEDGE.items():
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

    project = DirectoryProject(root, prefix=PurePosixPath('project'))
    library = PredefinedProjectLibrary({'project': project})

    project_env = env[ProjectEnv]
    project_env.configure(library)
    project_env.add('project')

    return env

def test_no_match(tmp_path):
    env = create_env(tmp_path)
    assert not handle_wildcard_retrieval_command('e/*.txt', env)
    assert not env[RetrievalsEnv].get()

def test_no_wildcard(tmp_path):
    env = create_env(tmp_path)
    assert not handle_wildcard_retrieval_command('project/a/b.txt', env)
    assert not env[RetrievalsEnv].get()

def test_no_slash(tmp_path):
    env = create_env(tmp_path)
    assert handle_wildcard_retrieval_command('project/*.txt', env)
    # The order is not guaranteed here as keys() returns set-like behavior
    # but we are checking content equality
    assert env[RetrievalsEnv].get() == KnowledgeIndex([PurePosixPath('project/d.txt')])

def test_single_match(tmp_path):
    env = create_env(tmp_path)
    assert handle_wildcard_retrieval_command('project/x/y/*.txt', env)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([PurePosixPath('project/x/y/z.txt')])

def test_multiple_matches(tmp_path):
    env = create_env(tmp_path)
    assert handle_wildcard_retrieval_command('project/a/*.txt', env)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([PurePosixPath('project/a/b.txt'), PurePosixPath('project/a/c.txt')])

def test_tilde_path_match(tmp_path):
    env = create_env(tmp_path)
    assert handle_wildcard_retrieval_command('~/project/a/*.txt', env)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([PurePosixPath('project/a/b.txt'), PurePosixPath('project/a/c.txt')])

def test_absolute_path_fails(tmp_path):
    env = create_env(tmp_path)
    assert not handle_wildcard_retrieval_command('/a/*.txt', env)
    assert not env[RetrievalsEnv].get()

def test_deep_match(tmp_path):
    env = create_env(tmp_path)
    assert handle_wildcard_retrieval_command('**/*.txt', env)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([
        PurePosixPath('project/a/b.txt'),
        PurePosixPath('project/a/c.txt'),
        PurePosixPath('project/d.txt'),
        PurePosixPath('project/x/y/z.txt')
    ])

def test_invalid_characters(tmp_path):
    env = create_env(tmp_path)
    assert not handle_wildcard_retrieval_command('a/*.txt$', env)
    assert not env[RetrievalsEnv].get()
