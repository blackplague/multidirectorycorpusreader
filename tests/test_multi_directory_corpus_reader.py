from typing import List

import os
import pytest

from multidirectorycorpusreader.multidirectorycorpusreader import MultiDirectoryCorpusReader


@pytest.fixture
def default_sources_mdcr():
    source1 = 'tests/data/source1'
    source2 = 'tests/data/source2'

    mdcr = MultiDirectoryCorpusReader(source_directories=[source1, source2], glob_filters=['*.txt', '*.msg'])
    yield source1, source2, mdcr


def test_initialization(default_sources_mdcr):
    source1, source2, mdcr = default_sources_mdcr

    expected_result: List[str] = sorted([os.path.join(source1, p) for p in os.listdir(source1)]
                                        + [os.path.join(source2, p) for p in os.listdir(source2)]) # noqa W503

    result = sorted(mdcr.files)

    assert expected_result == result
    assert len(expected_result) == len(result)


def test_len_dunder(default_sources_mdcr):
    source1, source2, mdcr = default_sources_mdcr

    expected_result: int = len(sorted([os.path.join(source1, p) for p in os.listdir(source1)]
                                      + [os.path.join(source2, p) for p in os.listdir(source2)])) # noqa W503

    result: int = len(mdcr)

    assert expected_result == result


def test_preprocessor_func(default_sources_mdcr):
    source1, source2, _ = default_sources_mdcr

    def preprocessor_tokenize_remove_a(s: str) -> List[str]:
        return s.replace('a', '').split(' ')

    mdcr = MultiDirectoryCorpusReader(
        source_directories=[source1, source2],
        glob_filters=['*.txt', '*.msg'],
        preprocess_function=preprocessor_tokenize_remove_a)
    # Test that all tokenized documents have a length larger than 0 and that none of the tokens contains 'a'
    for res in mdcr:
        assert len(res) > 0
        assert all(['a' not in token for token in res])


def test_read_single_file_streaming():
    source = 'tests/data/source1'
    glob_filter = '1.txt'

    with open(f'{source}/{glob_filter}', 'r') as fd:
        expected_result = fd.read()

    result = next(iter(mdcr))

    mdcr = MultiDirectoryCorpusReader(source_directories=[source], glob_filters=[glob_filter])
    assert expected_result == result


def test_read_single_file_in_memory():
    source = 'tests/data/source1'
    glob_filter = '1.txt'

    with open(f'{source}/{glob_filter}', 'r') as fd:
        expected_result = fd.read()

    result = next(iter(mdcr))

    mdcr = MultiDirectoryCorpusReader(source_directories=[source], glob_filters=[glob_filter], in_memory=True)
    assert expected_result == result


def test_repeatability_in_memory():
    source = 'tests/data/source1'
    glob_filter = '1.txt'

    with open(f'{source}/{glob_filter}', 'r') as fd:
        expected_result = fd.read()


    mdcr = MultiDirectoryCorpusReader(source_directories=[source], glob_filters=[glob_filter], in_memory=True)
    mdcr_iter = iter(mdcr)
    result = next(mdcr_iter)

    assert expected_result == result

    mdcr_iter = iter(mdcr)
    new_result = next(mdcr_iter)

    assert expected_result == new_result


def test_repeatability_streaming():
    source = 'tests/data/source1'
    glob_filter = '1.txt'

    with open(f'{source}/{glob_filter}', 'r') as fd:
        expected_result = fd.read()


    mdcr = MultiDirectoryCorpusReader(source_directories=[source], glob_filters=[glob_filter], in_memory=False)
    mdcr_iter = iter(mdcr)
    result = next(mdcr_iter)

    assert expected_result == result

    mdcr_iter = iter(mdcr)
    new_result = next(mdcr_iter)

    assert expected_result == new_result
