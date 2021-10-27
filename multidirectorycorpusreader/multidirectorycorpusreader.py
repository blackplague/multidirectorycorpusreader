from glob import glob
from itertools import chain, product
from typing import Callable, List, Optional


import os
import logging

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO)


class MultiDirectoryCorpusReader:
    def __init__(self,
                 input_dirs: List[str],
                 glob_filters: List[str],
                 preprocessor_func: Optional[Callable[[str], List[str]]]=None,
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
        self.preprocessor_func = preprocessor_func
        self._files = list(chain(*[glob(os.path.join(p, gf)) for p, gf in product(input_dirs, glob_filters)]))
        logging.info(f'Found #{len(self.files)} files')

    def __iter__(self):
        for i, f in enumerate(self.files):
            if self.print_progress and i > 0 and i % 10000 == 0:
                logging.info(f"Read {i} files")
            with open(f, 'r') as fd:
                content = fd.read()
                if content == '':
                    continue
                if self.preprocessor_func is None:
                    yield content
                else:
                    yield self.preprocessor_func(content)

    def __len__(self):
        return len(self.files)

    @property
    def files(self):
        return self._files
