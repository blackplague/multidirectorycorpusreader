import pathlib
from setuptools import setup, find_packages

FILE_LOCATION = pathlib.Path(__file__).parent
README = (FILE_LOCATION / 'README.md').read_text()

setup(
    name='MultiDirectoryCorpusReader',
    version='0.2.0',
    description='Easier multi directory source globbing of text files',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Michael Andersen',
    author_email='gosuckadeadcow+github@gmail.com',
    url='https://github.com/blackplague/multidirectorycorpusreader',
    packages=find_packages(exclude=('tests')),
)
