from __future__ import annotations
from datetime import datetime
from pathlib import Path
import logging
import llobot.time
from llobot.knowledge import Knowledge
from llobot.knowledge.archives import KnowledgeArchive
from llobot.knowledge.subsets import KnowledgeSubset
import llobot.knowledge.subsets
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.sources import KnowledgeSource

_logger = logging.getLogger(__name__)

# Project usually corresponds to single git repository or a directory of related files.
# This is an abstract class to allow for future extensions.
class Project:
    # Project name, usually corresponding to git repository name.
    @property
    def name(self) -> str:
        raise NotImplementedError

    # This should be mostly unfiltered fetch of the whole project. Scope objects will narrow it down.
    @property
    def source(self) -> KnowledgeSource:
        raise NotImplementedError

    # Archive used to store snapshots of this project among other projects.
    @property
    def archive(self) -> KnowledgeArchive:
        return llobot.knowledge.archives.standard()

    # Root scope spanning the whole project. Root of the scope tree.
    @property
    def scope(self) -> Scope:
        return _SimpleRootScope(self)

    def find(self, name: str) -> Scope | None:
        return self.scope.find(name)

    def knowledge(self, cutoff: datetime | None = None) -> Knowledge:
        return self.archive.last(self.name, cutoff)

    def fetch(self) -> Knowledge:
        return self.source.load_all()

    def refresh(self):
        fresh = self.fetch()
        if fresh != self.knowledge():
            self.archive.add(self.name, llobot.time.now(), fresh)
            _logger.info(f"Refreshed: {self.name}")
        else:
            _logger.info(f"Refreshed (no change): {self.name}")

# Scope objects form a tree with the root scope covering the whole project.
# This is an abstract class to allow for future extensions.
class Scope:
    @property
    def project(self) -> Project:
        raise NotImplementedError

    # Globally unique scope name. It is not appended to project name,
    # so this should usually include project name as a prefix, but there could be exceptions,
    # for example when a uniquely named subproject is nested in another project's repository.
    @property
    def name(self) -> str:
        raise NotImplementedError

    # This is None only for the root project-wide scope.
    @property
    def parent(self) -> Scope | None:
        return None

    @property
    def ancestry(self) -> list[Scope]:
        return [self] + self.parent.ancestry if self.parent else [self]

    # Child order should not matter, but we expose children as a list for convenience and performance.
    @property
    def children(self) -> list[Scope]:
        return []

    # Determines which parts of the project are included in the scope.
    # Parent subset is not automatically used to prefilter the project, so this must not rely on it.
    @property
    def subset(self) -> KnowledgeSubset:
        return llobot.knowledge.subsets.everything()

    def find(self, name: str) -> Scope | None:
        if self.name == name:
            return self
        for child in self.children:
            found = child.find(name)
            if found:
                return found
        return None

    def knowledge(self, cutoff: datetime | None = None) -> Knowledge:
        return self.project.knowledge(cutoff) & self.subset

# Scope templates are created without project or parent, because they are usually instantiated bottom up.
# Top-down template expansion process returns scope with the two properties filled in.
# This is an abstract class to allow for future extensions.
class ScopeTemplate:
    # Returns expanded scope for the current scope template.
    # Information from the project and the parent can be used to complete the template.
    def expand(self, project: Project, parent: Scope | None) -> Scope:
        raise NotImplementedError

class _SimpleRootScope(Scope):
    _project: Project

    def __init__(project: Project):
        self._project = project

    @property
    def project(self) -> Project:
        return self._project

    @property
    def name(self) -> str:
        return self.project.name

class _StandardScope(Scope):
    _project: Project
    _name: str
    _parent: Scope | None
    _children: list[Scope]
    _subset: KnowledgeSubset

    def __init__(
        self,
        project: Project,
        name: str,
        parent: Scope | None,
        children: list[ScopeTemplate],
        subset: KnowledgeSubset
    ):
        self._project = project
        self._name = name
        self._parent = parent
        self._subset = subset
        self._children = sorted([child.expand(project, self) for child in children], key=lambda x: x.name)

    @property
    def project(self) -> Project:
        return self._project

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent(self) -> Scope | None:
        return self._parent

    @property
    def children(self) -> list[Scope]:
        return self._children

    @property
    def subset(self) -> KnowledgeSubset:
        return self._subset

def scope(project: Project, name: str | None = None, subset: KnowledgeSubset = llobot.knowledge.subsets.everything(), parent: Scope | None = None, children: list[ScopeTemplate] = []) -> Scope:
    return _StandardScope(project, name or project.name, parent, children, subset)

class _StandardScopeTemplate(ScopeTemplate):
    # If the name starts with a dash, it is appended to parent or project name during template expansion.
    # If the name is empty, project name will be used unmodified, which is useful for root scope.
    _name: str
    _children: list[ScopeTemplate]
    # Combined with parent for convenience.
    _subset: KnowledgeSubset

    def __init__(self, name: str, children: list[ScopeTemplate], subset: KnowledgeSubset):
        self._name = name
        self._children = children
        self._subset = subset

    def expand(self, project: Project, parent: Scope | None) -> Scope:
        if not self._name:
            name = project.name
        elif self._name.startswith('-'):
            name = (parent.name if parent else project.name) + self._name
        else:
            name = self._name
        subset = self._subset & parent.subset if parent else self._subset
        return scope(project, name, subset, parent, self._children)

def scope_template(name: str = '', subset: KnowledgeSubset | str | Path | KnowledgeIndex = llobot.knowledge.subsets.everything(), children: list[ScopeTemplate] = []) -> ScopeTemplate:
    return _StandardScopeTemplate(name, children, llobot.knowledge.subsets.coerce(subset))

class _StandardProject(Project):
    _name: str
    _source: KnowledgeSource
    _archive: KnowledgeArchive
    _scope: Scope

    def __init__(self, name: str, source: KnowledgeSource, archive: KnowledgeArchive, scope: ScopeTemplate):
        self._name = name
        self._source = source
        self._archive = archive
        self._scope = scope.expand(self, None)

    @property
    def name(self) -> str:
        return self._name

    @property
    def source(self) -> KnowledgeSource:
        return self._source

    @property
    def archive(self) -> KnowledgeArchive:
        return self._archive

    @property
    def scope(self) -> Scope:
        return self._scope

def project(name: str, source: KnowledgeSource, archive: KnowledgeArchive = llobot.knowledge.archives.standard(), scope: ScopeTemplate = scope_template()) -> Project:
    return _StandardProject(name, source, archive, scope)

def _subtree(name: str, specification: dict | KnowledgeSubset | KnowledgeIndex | Path | str) -> ScopeTemplate:
    if isinstance(specification, dict):
        if '' not in specification:
            raise ValueError(f'Missing subset specification for {name}.')
        return scope_template(name, llobot.knowledge.subsets.coerce(specification['']), [_subtree(name, subspec) for name, subspec in specification.items() if name != ''])
    else:
        return scope_template(name, llobot.knowledge.subsets.coerce(specification))

def create(
    name: str,
    source: KnowledgeSource,
    archive: KnowledgeArchive = llobot.knowledge.archives.standard(),
    # Dictionary keys are scope object names. Names starting with dash are appended to parent/project name.
    # Special key '' (empty string) refers to the current scope object.
    # Dictionary values are either subset specifications or dict objects describing nested scope objects.
    # Subset specifications are combined with parent subset, so nested scope objects don't have to repeat them.
    scope: dict | KnowledgeSubset | KnowledgeIndex | Path | str = llobot.knowledge.subsets.everything()
) -> Project:
    if isinstance(scope, dict) and not '' in scope:
        scope = scope.copy()
        scope[''] = llobot.knowledge.subsets.everything()
    return project(name, source, archive, _subtree(name, scope))

__all__ = [
    'Project',
    'Scope',
    'ScopeTemplate',
    'scope',
    'scope_template',
    'project',
    'create',
]

