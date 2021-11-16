# MultiDirectoryCorpusReader

MultiDirectoryCorpusReader provides an easy iterator for multi directory source globbing of raw
text files which can be used either streaming or in memory.

## Installation

It can be installed directly from github using:

```sh
#> python -m pip install git+https://github.com/blackplague/multidirectorycorpusreader.git
```

## Usage example

The minimum viable usage is to supply a list of source directories and a list of globbing filters.

```python
mdcr = MultiDirectoryCorpusReader(
    source_directories=['data/source1', 'data/source2'],
    glob_filters=['*.txt', '*.msg', '*.doc', '*.text'])
```

It is possible to pass a preprocess function to the script, this could for example be the
*simple_preprocess* function from the [Gensim][gensim-url] library. This will also print the progress
during the streaming of the files.

```python
from gensim.utils import simple_preprocess

mdcr = MultiDirectoryCorpusReader(
    source_directories=['data/source1', 'data/source2'],
    glob_filters=['*.txt', '*.msg', '*.doc', '*.text'],
    preprocess_function=simple_preprocess,
    print_progress=True)
```

This example shows how to supply a preprocess function that you have written yourself. In addition
this will also read all files into memory and print progress during.

```python
def preprocessor_tokenize_remove_a(s: str) -> List[str]:
    return s.replace('a', '').split(' ')

mdcr = MultiDirectoryCorpusReader(
    source_directories=['data/source1', 'data/source2'],
    glob_filters=['*.txt', '*.msg', '*.doc', '*.text'],
    preprocess_function=preprocessor_tokenize_remove_a,
    in_memory=True,
    print_progress=True)
```

## Release History

* 0.2.0
  * The first proper release

## Meta

Michael Andersen - michael10andersen+mdcr -[at]- gmail.com - [Github](https://github.com/blackplague/)

Distributed under the XYZ license. See ``LICENSE`` for more information.

<!-- Markdown link & img dfn's -->
[gensim-url]: https://radimrehurek.com/gensim/
