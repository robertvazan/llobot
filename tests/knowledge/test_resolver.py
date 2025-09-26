from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.resolver import KnowledgeResolver, cached_knowledge_resolver

def test_resolver_creation():
    index = KnowledgeIndex([
        Path('src/main.py'),
        Path('src/utils/helper.py'),
        Path('test/test_main.py'),
        Path('README.md'),
    ])
    resolver = KnowledgeResolver(index)

    # Test names mapping
    assert Path('src/main.py') in resolver._names['main.py']
    assert Path('test/test_main.py') in resolver._names['test_main.py']
    assert Path('README.md') in resolver._names['README.md']

    # Test tails mapping
    assert Path('src/utils/helper.py') in resolver._tails[Path('utils/helper.py')]

def test_create_resolver_from_knowledge():
    knowledge = Knowledge({Path('src/main.py'): 'content', Path('README.md'): 'content'})
    resolver = cached_knowledge_resolver(knowledge)
    assert isinstance(resolver, KnowledgeResolver)

def test_create_resolver_from_index():
    index = KnowledgeIndex([Path('src/main.py'), Path('README.md')])
    resolver = cached_knowledge_resolver(index)
    assert isinstance(resolver, KnowledgeResolver)

def test_create_resolver_from_ranking():
    ranking = KnowledgeRanking([Path('src/main.py'), Path('README.md')])
    resolver = cached_knowledge_resolver(ranking)
    assert isinstance(resolver, KnowledgeResolver)

def test_resolve_all():
    index = KnowledgeIndex([
        Path('src/main.py'),
        Path('src/utils/helper.py'),
        Path('test/main.py'),
    ])
    resolver = KnowledgeResolver(index)
    assert resolver.resolve_all(Path('main.py')) == KnowledgeIndex(['src/main.py', 'test/main.py'])
    assert resolver.resolve_all(Path('utils/helper.py')) == KnowledgeIndex(['src/utils/helper.py'])
    assert resolver.resolve_all(Path('nonexistent.py')) == KnowledgeIndex()
    assert resolver.resolve_all(Path('main.py'), Path('helper.py')) == KnowledgeIndex(['src/main.py', 'test/main.py', 'src/utils/helper.py'])

def test_resolve():
    index = KnowledgeIndex([
        Path('src/main.py'),
        Path('src/utils/helper.py'),
        Path('test/main.py'),
    ])
    resolver = KnowledgeResolver(index)
    assert resolver.resolve(Path('main.py')) is None
    assert resolver.resolve(Path('utils/helper.py')) == Path('src/utils/helper.py')
    assert resolver.resolve(Path('helper.py')) == Path('src/utils/helper.py')
    assert resolver.resolve(Path('nonexistent.py')) is None

def test_resolve_all_near():
    index = KnowledgeIndex([
        Path('src/main.py'),
        Path('src/utils/helper.py'),
        Path('test/main.py'),
        Path('test/utils/helper.py'),
    ])
    resolver = KnowledgeResolver(index)
    # Disambiguation
    assert resolver.resolve_all_near(Path('src/some_other_file.py'), Path('main.py')) == KnowledgeIndex(['src/main.py'])
    assert resolver.resolve_all_near(Path('test/some_other_file.py'), Path('main.py')) == KnowledgeIndex(['test/main.py'])
    # Tie
    assert resolver.resolve_all_near(Path('root.py'), Path('main.py')) == KnowledgeIndex(['src/main.py', 'test/main.py'])
    # Single result
    assert resolver.resolve_all_near(Path('src'), Path('utils/helper.py')) == KnowledgeIndex(['src/utils/helper.py'])

def test_resolve_near():
    index = KnowledgeIndex([
        Path('src/main.py'),
        Path('src/utils/helper.py'),
        Path('test/main.py'),
    ])
    resolver = KnowledgeResolver(index)
    # Disambiguation
    assert resolver.resolve_near(Path('src/other.py'), Path('main.py')) == Path('src/main.py')
    assert resolver.resolve_near(Path('test/other.py'), Path('main.py')) == Path('test/main.py')
    # No match
    assert resolver.resolve_near(Path('src/other.py'), Path('nonexistent.py')) is None
    # Tie
    assert resolver.resolve_near(Path('root.py'), Path('main.py')) is None
