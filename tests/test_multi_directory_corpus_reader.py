from typing import List

import os
import pytest

from multidirectorycorpusreader.multidirectorycorpusreader import MultiDirectoryCorpusReader


@pytest.fixture
def default_sources_mdcr():
    source1 = 'tests/data/source1'
    source2 = 'tests/data/source2'

    mdcr = MultiDirectoryCorpusReader(input_dirs=[source1, source2], glob_filters=['*.txt', '*.msg'])
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
        input_dirs=[source1, source2],
        glob_filters=['*.txt', '*.msg'],
        preprocessor_func=preprocessor_tokenize_remove_a)
    # Test that all tokenized documents have a length larger than 0 and that none of the tokens contains 'a'
    for res in mdcr:
        assert len(res) > 0
        assert all(['a' not in token for token in res])
