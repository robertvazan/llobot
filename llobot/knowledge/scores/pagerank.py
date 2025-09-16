"""
Scorers based on the PageRank algorithm over the knowledge graph.
"""
from __future__ import annotations
from functools import lru_cache
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs import KnowledgeGraph
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.rankings import rank_lexicographically
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.scorers import KnowledgeScorer
from llobot.knowledge.scores.constant import constant_scores
from llobot.scrapers import GraphScraper, standard_scraper
from llobot.utils.values import ValueTypeMixin

@lru_cache(maxsize=2)
def pagerank_scores(
    graph: KnowledgeGraph,
    nodes: KnowledgeIndex = KnowledgeIndex(),
    initial: KnowledgeScores = KnowledgeScores(),
    *,
    damping: float = 0.85,
    iterations: int = 100,
    tolerance: float = 1.0e-3
) -> KnowledgeScores:
    """
    Calculates PageRank scores for documents in a knowledge graph.

    Args:
        graph: The knowledge graph to run PageRank on.
        nodes: An optional set of nodes to include, even if not in the graph.
        initial: Initial scores to start with. If empty, uniform scores are used.
        damping: The damping factor for PageRank.
        iterations: The maximum number of iterations to run.
        tolerance: The convergence tolerance.

    Returns:
        The calculated PageRank scores.
    """
    if not graph and not nodes:
        return KnowledgeScores()
    # This implementation is optimized to use Python's built-in types and integer-addressed lists,
    # because the neat version using our high-level classes was too slow.
    backlinks = graph.reverse()
    nodes = nodes | graph.keys() | backlinks.keys()
    ranking = list(rank_lexicographically(nodes))
    path_ids = {path: i for i, path in enumerate(ranking)}
    count = len(ranking)
    graph_table = [tuple(path_ids[target] for target in graph[source]) for source in ranking]
    backlinks_table = [tuple(path_ids[source] for source in backlinks[target]) for target in ranking]
    sinks = [i for i, targets in enumerate(graph_table) if not targets]
    if initial:
        initial_norm = count / initial.total() if initial.total() else 0
        initial_table = [initial[path] * initial_norm for path in ranking] if initial_norm else [1.0] * count
    else:
        initial_table = [1.0] * count
    scores = initial_table
    for _ in range(iterations):
        new_scores = [0.0] * count
        sink_spread = sum(scores[source] for source in sinks) / count if count else 0
        for target in range(count):
            incoming = initial_table[target] * sink_spread
            for source in backlinks_table[target]:
                targets = graph_table[source]
                if targets:
                    incoming += scores[source] / len(targets)
            new_scores[target] = (1 - damping) * initial_table[target] + damping * incoming
        delta = sum(abs(new_scores[i] - scores[i]) for i in range(count)) / count if count else 0
        scores = new_scores
        if delta < tolerance:
            break
    return KnowledgeScores({ranking[i]: scores[i] for i in range(count)})

class PageRankScorer(KnowledgeScorer, ValueTypeMixin):
    """
    A scorer that uses the PageRank algorithm on the knowledge graph.
    """
    _scraper: GraphScraper
    _damping: float
    _iterations: int
    _tolerance: float

    def __init__(self,
        scraper: GraphScraper = standard_scraper(),
        damping: float = 0.85,
        iterations: int = 100,
        tolerance: float = 1.0e-3
    ):
        """
        Initializes the PageRank scorer.

        Args:
            scraper: The scraper to use for building the knowledge graph.
            damping: The damping factor for the PageRank algorithm.
            iterations: The maximum number of iterations to perform.
            tolerance: The tolerance for convergence.
        """
        self._scraper = scraper
        self._damping = damping
        self._iterations = iterations
        self._tolerance = tolerance

    def score(self, knowledge: Knowledge) -> KnowledgeScores:
        """
        Calculates PageRank scores for the knowledge, starting from uniform initial scores.

        Args:
            knowledge: The knowledge base to score.

        Returns:
            The calculated PageRank scores.
        """
        return self.rescore(knowledge, constant_scores(knowledge))

    def rescore(self, knowledge: Knowledge, initial: KnowledgeScores) -> KnowledgeScores:
        """
        Calculates PageRank scores, starting from a given set of initial scores.

        It first scrapes the knowledge to build a graph, then runs the PageRank
        algorithm on it.

        Args:
            knowledge: The knowledge base to score.
            initial: The initial scores to use for the PageRank calculation.

        Returns:
            The calculated PageRank scores.
        """
        graph = self._scraper.scrape(knowledge)
        return pagerank_scores(
            graph,
            knowledge.keys(),
            initial,
            damping=self._damping,
            iterations=self._iterations,
            tolerance=self._tolerance
        )

__all__ = [
    'pagerank_scores',
    'PageRankScorer',
]
