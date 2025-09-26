from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.graphs.java import JavaPascalCaseCrawler

def test_java_pascal_case_crawler():
    knowledge = Knowledge({
        Path('src/com/example/Main.java'): """
            package com.example;
            import com.example.util.Helper;
            // A comment with AnotherClass
            class Main {
                void main() {
                    new Helper();
                    String s = "SomeString";
                    /* BlockComment with ThirdClass */
                }
            }
        """,
        Path('src/com/example/util/Helper.java'): """
            package com.example.util;
            public class Helper {}
        """,
    })
    crawler = JavaPascalCaseCrawler()
    graph = crawler.crawl(knowledge)
    assert len(graph) == 1
    assert list(graph.keys().sorted()) == [Path('src/com/example/Main.java')]
    targets = graph[Path('src/com/example/Main.java')].sorted()
    assert list(targets) == [Path('src/com/example/util/Helper.java')]
