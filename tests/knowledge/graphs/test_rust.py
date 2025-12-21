from pathlib import PurePosixPath
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs.rust import RustSubmoduleCrawler, RustUseCrawler

KNOWLEDGE = Knowledge({
    PurePosixPath('src/main.rs'): "mod utils;\nuse crate::utils::helpers;",
    PurePosixPath('src/utils/mod.rs'): "pub mod helpers;",
    PurePosixPath('src/utils/helpers.rs'): "use super::constants;",
    PurePosixPath('src/utils/constants.rs'): "",
})

def test_rust_submodule_crawler():
    crawler = RustSubmoduleCrawler()
    graph = crawler.crawl(KNOWLEDGE)
    assert list(graph[PurePosixPath('src/main.rs')].sorted()) == [PurePosixPath('src/utils/mod.rs')]
    assert list(graph[PurePosixPath('src/utils/mod.rs')].sorted()) == [PurePosixPath('src/utils/helpers.rs')]

def test_rust_use_crawler():
    crawler = RustUseCrawler()
    graph = crawler.crawl(KNOWLEDGE)
    assert list(graph[PurePosixPath('src/main.rs')].sorted()) == [PurePosixPath('src/utils/helpers.rs')]
    assert list(graph[PurePosixPath('src/utils/helpers.rs')].sorted()) == [PurePosixPath('src/utils/constants.rs')]
