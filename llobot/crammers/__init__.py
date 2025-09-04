"""
Components for selecting information to fit into a context budget.

This package provides "crammers," which are responsible for selecting the most
relevant information (such as examples, knowledge documents, or file indexes)
to fit within a given context size budget for an LLM prompt.

Crammers
--------
EditCrammer
    Combines examples with updates of documents those examples touch.
ExampleCrammer
    Selects a set of recent examples that fit within a budget.
IndexCrammer
    Formats file indexes, deciding whether to include them based on budget.
KnowledgeCrammer
    Selects a subset of knowledge documents based on scores and budget.
"""
