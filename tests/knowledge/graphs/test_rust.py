from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs.rust import RustSubmoduleCrawler, RustUseCrawler

KNOWLEDGE = Knowledge({
    Path('src/main.rs'): "mod utils;\nuse crate::utils::helpers;",
    Path('src/utils/mod.rs'): "pub mod helpers;",
    Path('src/utils/helpers.rs'): "use super::constants;",
    Path('src/utils/constants.rs'): "",
})

def test_rust_submodule_crawler():
    crawler = RustSubmoduleCrawler()
    graph = crawler.crawl(KNOWLEDGE)
    assert list(graph[Path('src/main.rs')].sorted()) == [Path('src/utils/mod.rs')]
    assert list(graph[Path('src/utils/mod.rs')].sorted()) == [Path('src/utils/helpers.rs')]

def test_rust_use_crawler():
    crawler = RustUseCrawler()
    graph = crawler.crawl(KNOWLEDGE)
    assert list(graph[Path('src/main.rs')].sorted()) == [Path('src/utils/helpers.rs')]
    assert list(graph[Path('src/utils/helpers.rs')].sorted()) == [Path('src/utils/constants.rs')]
