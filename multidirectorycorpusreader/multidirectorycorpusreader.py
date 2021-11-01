from glob import glob
from itertools import chain, product
import multiprocessing as mp
from typing import Callable, List, Optional


import os
import logging

logging.basicConfig(
    format='%(asctime)s:%(levelname)s: %(message)s',
    level=logging.INFO)


class MultiDirectoryCorpusReader:
    def __init__(self,
                 source_directories: List[str],
                 glob_filters: List[str],
                 preprocess_function: Optional[Callable[[str], List[str]]]=None,
                 in_memory: bool=False,
                 print_progress: bool=False):
        """MultiDictionaryCorpusReader

        Usage: Streams **raw text** content from multiple directories using globbing for matching
        file types.

        Example 1, given the directory structure:

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

        mdcr = MultiDirectoryCorpusReader(input_dirs=['data/source1', 'data/source2'],
                                          glob_filters=['*.txt', '*.msg', '*.doc', '*.text'])

        The above provides an iterator that yields the text content of all files ending with txt,
        msg, doc and text in the source1 and source2 directories. In addition it supports passing
        a preprocess function which is applied to the raw text read from the files.

        Example 2, passing a preprocess function and logging progress

        from gensim.utils import simple_preprocess

        mdcr = MultiDirectoryCorpusReader(
            input_dirs=['data/source1', 'data/source2'],
            glob_filters=['*.txt', '*.msg', '*.doc', '*.text'],
            preprocess_func=simple_preprocess,
            print_progress=True)
        """
        self.print_progress = print_progress
        self.preprocess_function = preprocess_function
        self.in_memory = in_memory
        self._filenames = list(chain(*[glob(os.path.join(p, gf)) for p, gf in product(source_directories, glob_filters)]))
        if self.print_progress:
            logging.info(f'Found #{len(self.files)} files')
        # Generator expression (delayed file reading)
        # self._files = (self._read_file(f) for f in self._filenames)
        if self.in_memory:
            if self.print_progress:
                logging.info('Reading files into memory, please wait...')
            num_workers = mp.cpu_count() - 1
            pool = mp.Pool(processes=num_workers)
            self._files = sorted(pool.map(self._read_file, self.files))

    @property
    def files(self):
        return self._filenames

    def __len__(self):
        return len(self._filenames)

    def __iter__(self):
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

    def _read_files_gen(self):
        return (self._read_file(f) for f in self.files)

    def _read_file(self, filename: str) -> str:
        with open(filename, 'r') as fd:
            content = fd.read()
            return content
