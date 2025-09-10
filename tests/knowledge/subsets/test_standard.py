from pathlib import Path
from llobot.knowledge.subsets.standard import (
    ancillary_subset,
    blacklist_subset,
    boilerplate_subset,
    overviews_subset,
    whitelist_subset,
)

def test_ancillary_subset():
    ancillary = ancillary_subset()
    assert Path('test/some_test.py') in ancillary
    assert Path('resources/data.xml') in ancillary
    assert Path('jest.config.js') in ancillary
    assert Path('README.md') not in ancillary
    assert Path('.gitignore') in ancillary

def test_blacklist_subset():
    blacklist = blacklist_subset()
    assert Path('.git/config') in blacklist
    assert Path('node_modules/dep/index.js') in blacklist
    assert Path('target/classes/Main.class') in blacklist
    assert Path('src/main.py') not in blacklist

def test_boilerplate_subset():
    boilerplate = boilerplate_subset()
    assert Path('.gitignore') in boilerplate
    assert Path('LICENSE') in boilerplate
    assert Path('README.md') not in boilerplate

def test_overviews_subset():
    overviews = overviews_subset()
    assert Path('README.md') in overviews
    assert Path('__init__.py') in overviews
    assert Path('pom.xml') in overviews
    assert Path('src/main.py') not in overviews

def test_whitelist_subset():
    whitelist = whitelist_subset()
    assert Path('src/main.py') in whitelist
    assert Path('README.md') in whitelist
    assert Path('image.png') not in whitelist
