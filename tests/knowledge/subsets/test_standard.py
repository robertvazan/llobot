from pathlib import PurePosixPath
from llobot.knowledge.subsets.standard import (
    ancillary_subset,
    blacklist_subset,
    boilerplate_subset,
    overviews_subset,
    whitelist_subset,
)

def test_ancillary_subset():
    ancillary = ancillary_subset()
    assert PurePosixPath('test/some_test.py') in ancillary
    assert PurePosixPath('resources/data.xml') in ancillary
    assert PurePosixPath('jest.config.js') in ancillary
    assert PurePosixPath('README.md') not in ancillary
    assert PurePosixPath('.gitignore') in ancillary

def test_blacklist_subset():
    blacklist = blacklist_subset()
    assert PurePosixPath('.git/config') in blacklist
    assert PurePosixPath('node_modules/dep/index.js') in blacklist
    assert PurePosixPath('target/classes/Main.class') in blacklist
    assert PurePosixPath('src/main.py') not in blacklist

def test_boilerplate_subset():
    boilerplate = boilerplate_subset()
    assert PurePosixPath('.gitignore') in boilerplate
    assert PurePosixPath('LICENSE') in boilerplate
    assert PurePosixPath('README.md') not in boilerplate

def test_overviews_subset():
    overviews = overviews_subset()
    assert PurePosixPath('README.md') in overviews
    assert PurePosixPath('__init__.py') in overviews
    assert PurePosixPath('pom.xml') in overviews
    assert PurePosixPath('src/main.py') not in overviews

def test_whitelist_subset():
    whitelist = whitelist_subset()
    assert PurePosixPath('src/main.py') in whitelist
    assert PurePosixPath('README.md') in whitelist
    assert PurePosixPath('image.png') not in whitelist
