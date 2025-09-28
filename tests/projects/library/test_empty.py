from llobot.projects.library.empty import EmptyProjectLibrary

def test_empty_project_library():
    lib = EmptyProjectLibrary()
    assert lib.lookup('any') == []
    assert lib == EmptyProjectLibrary()
