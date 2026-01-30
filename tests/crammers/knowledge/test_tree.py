from pathlib import PurePosixPath
from llobot.crammers.knowledge.tree import RootKnowledgeCrammer
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.predefined import PredefinedProjectLibrary

def test_root_knowledge_crammer(tmp_path):
    # Setup test environment
    (tmp_path / 'README.md').write_text('# README')
    (tmp_path / 'CONTRIBUTING.md').write_text('# Contributing')
    (tmp_path / 'other.txt').write_text('Other file')
    (tmp_path / 'subdir').mkdir()
    (tmp_path / 'subdir' / 'README.md').write_text('# Subdir README')

    # Force a known prefix 'test'
    project = DirectoryProject(tmp_path, prefix='test')
    env = Environment()
    env[ProjectEnv].configure(PredefinedProjectLibrary({'test': project}))
    env[ProjectEnv].add('test')

    # Run crammer
    crammer = RootKnowledgeCrammer()
    crammer.cram(env)

    # Verify results
    knowledge = env[KnowledgeEnv].keys()
    assert PurePosixPath('test/README.md') in knowledge
    assert PurePosixPath('test/CONTRIBUTING.md') in knowledge
    assert PurePosixPath('test/other.txt') not in knowledge
    assert PurePosixPath('test/subdir/README.md') not in knowledge

    # Verify context content
    thread = env[ContextEnv].build()
    content = '\n'.join(m.content for m in thread.messages)
    assert '# README' in content
    assert '# Contributing' in content

    # Run again, should not add duplicates
    initial_length = len(thread.messages)
    crammer.cram(env)
    assert len(env[ContextEnv].build().messages) == initial_length
