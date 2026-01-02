from llobot.projects.library.filtered import FilteredProjectLibrary
from llobot.projects.library.predefined import PredefinedProjectLibrary
from llobot.knowledge.subsets.pattern import PatternSubset
from llobot.projects.marker import MarkerProject

def test_filtered_project_library():
    p1 = MarkerProject('allowed/key')
    lib = PredefinedProjectLibrary({'allowed/key': p1})

    whitelist = PatternSubset("allowed/*")
    filtered_lib = FilteredProjectLibrary(lib, whitelist=whitelist)
    # also test operators
    assert isinstance(lib & whitelist, FilteredProjectLibrary)
    assert isinstance(lib - ~whitelist, FilteredProjectLibrary)

    assert filtered_lib.lookup("allowed/key") == [p1]
    assert filtered_lib.lookup("disallowed/key") == []

    # Invalid paths
    assert filtered_lib.lookup("/absolute/path") == []
    assert filtered_lib.lookup("path/with/../..") == []
