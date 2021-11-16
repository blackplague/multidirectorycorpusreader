from glob import glob
from itertools import chain, product
import multiprocessing as mp
from pathlib import Path
from typing import Callable, Generator, Iterator, List, Optional, Union


import os
import logging

logging.basicConfig(
    format='%(asctime)s:%(levelname)s: %(message)s',
    level=logging.INFO)


class MultiDirectoryCorpusReader:
    """Used for read raw text files from multi source directories
    using globbing filters. Able to either read all files into memory
    for usage via a Iterator or stream them from disk using a Generator

    Attributes
    ----------
    source_directories : List[str]
        a list of directories from which to read raw text files
    glob_filters : List[str]
        a list of globbing filters on which to match the text files,
        e.g. ['*.txt', '*.msg']
    preprocess_function : Callable[[str], List[str]], optional
        an optional preprocess function for cleaning the content of the
        text files (default is None)
    in_memory : bool
        should the file content be kept in memory or streamed from the
        sources (default is False)
    print_progress : bool
        display progress during operations, i.e. how many files in
        total, status every 10,000 files (default is False)


    Example
    -------
    Given the directory structure:

    data
    ├─ source1
    |  ├─ file1.txt
    |  ├─ file2.txt
    |  └─ file3.msg
    └─ source2
        ├─ file1.msg
        ├─ file2.doc
        ├─ file3.txt
        └─ file4.text

    mdcr = MultiDirectoryCorpusReader(
        source_directories=['data/source1', 'data/source2'],
        glob_filters=['*.txt', '*.msg', '*.doc', '*.text'])

    The above provides an iterator that yields the text content of all
    files ending with txt, msg, doc and text in the source1 and source2
    directories. In addition it supports passing a preprocess function
    which is applied to the raw text read from the files.

    Example
    -------
    Passing a preprocess function and logging progress

    from gensim.utils import simple_preprocess

    mdcr = MultiDirectoryCorpusReader(
        source_directories=['data/source1', 'data/source2'],
        glob_filters=['*.txt', '*.msg', '*.doc', '*.text'],
        preprocess_func=simple_preprocess,
        print_progress=True)
    """

    def __init__(self,
                 source_directories: List[str],
                 glob_filters: List[str],
                 preprocess_function: Optional[Callable[[str], List[str]]]=None,
                 in_memory: bool=False,
                 recursive: bool=False,
                 print_progress: bool=False):

        self.print_progress = print_progress
        self.preprocess_function = preprocess_function
        self.in_memory = in_memory
        if recursive:
            self._filenames = self._recursive(source_directories=source_directories, glob_filters=glob_filters)
        else:
            self._filenames = self._non_recursive(source_directories=source_directories, glob_filters=glob_filters)
        if self.print_progress:
            logging.info(f'Found #{len(self.files)} files')
        if self.in_memory:
            if self.print_progress:
                logging.info('Reading files into memory, please wait...')
            num_workers = mp.cpu_count() - 1
            pool = mp.Pool(processes=num_workers)
            self._files = sorted(pool.map(self._read_file, self.files))

    @property
    def files(self) -> List[str]:
        """Returns a list of files names that have been found using
        source_directories and glob_filters
        """
        return self._filenames

    def __len__(self) -> int:
        """Returns the number of filenames found"""
        return len(self._filenames)

    def __iter__(self) -> Iterator[Union[str, List[str]]]:
        """Returns an Iterator of either str or List[str] depending on
        whether or not a preprocess function is supplied"""
        if not self.in_memory:
            self._files = self._read_files_gen()

        for i, file_content in enumerate(self._files):
            if self.print_progress and i > 0 and i % 10000 == 0:
                logging.info(f"Read #{i} files")
            if file_content == '':
                continue
            if self.preprocess_function is None:
                yield file_content
            else:
                yield self.preprocess_function(file_content)

    def _read_files_gen(self) -> Generator[str, None, None]:
        """Returns Generator[str, None, None] that on consumption
        reads the content of a file on disk"""
        return (self._read_file(f) for f in self.files)

    def _read_file(self, filename: str) -> str:
        """Returns the content of a file on disk

        Parameters
        ----------
        filename : str
            Then name of the file to read from disk
        """
        with open(filename, 'r') as fd:
            content = fd.read()
            return content

    def _non_recursive(self, source_directories, glob_filters) -> List[str]:
        """Maybe also a bit too convoluted"""
        return list(map(str, chain(*[Path(path).glob(ext) for path in source_directories for ext in glob_filters])))

    def _recursive(self, source_directories, glob_filters) -> List[str]:
        """Maybe a bit to convoluted"""
        return list(map(str, chain(*[Path(path).rglob(ext) for path in source_directories for ext in glob_filters])))
