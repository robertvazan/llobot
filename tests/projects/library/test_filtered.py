from llobot.projects.library.filtered import FilteredProjectLibrary
from llobot.projects.library.zone import ZoneKeyedProjectLibrary
from llobot.knowledge.subsets.pattern import PatternSubset
from llobot.projects.zone import ZoneProject

def test_filtered_project_library():
    p1 = ZoneProject('allowed/key')
    lib = ZoneKeyedProjectLibrary(p1)

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
