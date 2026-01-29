from pathlib import PurePosixPath, Path
from llobot.commands.retrievals.solo import handle_solo_retrieval_command
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

def test_no_match(tmp_path):
    env = create_env(tmp_path, KNOWLEDGE)
    assert not handle_solo_retrieval_command('e.txt', env)
    assert not env[RetrievalsEnv].get()

def test_multiple_matches(tmp_path):
    knowledge = {
        PurePosixPath('a/b.txt'): 'content',
        PurePosixPath('x/b.txt'): 'another content',
    }
    env = create_env(tmp_path, knowledge)
    assert not handle_solo_retrieval_command('project/b.txt', env)
    assert not env[RetrievalsEnv].get()

def test_not_a_path(tmp_path):
    env = create_env(tmp_path, KNOWLEDGE)
    assert not handle_solo_retrieval_command('hello world', env)
    assert not env[RetrievalsEnv].get()

def test_invalid_characters(tmp_path):
    env = create_env(tmp_path, KNOWLEDGE)
    assert not handle_solo_retrieval_command('d.txt$', env)
    assert not env[RetrievalsEnv].get()

def test_exact_match(tmp_path):
    env = create_env(tmp_path, KNOWLEDGE)
    assert handle_solo_retrieval_command('project/d.txt', env)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([PurePosixPath('project/d.txt')])

def test_tilde_path_match(tmp_path):
    env = create_env(tmp_path, KNOWLEDGE)
    assert handle_solo_retrieval_command('~/project/a/b.txt', env)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([PurePosixPath('project/a/b.txt')])

def test_absolute_path_fails(tmp_path):
    env = create_env(tmp_path, KNOWLEDGE)
    assert not handle_solo_retrieval_command('/project/a/b.txt', env)
    assert not env[RetrievalsEnv].get()

def test_wildcard_is_ignored(tmp_path):
    env = create_env(tmp_path, KNOWLEDGE)
    assert not handle_solo_retrieval_command('a/*.txt', env)
    assert not env[RetrievalsEnv].get()
