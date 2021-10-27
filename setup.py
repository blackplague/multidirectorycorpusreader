from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='MultiDirectoryCorpusReader',
    version='0.1.0',
    description='Easier multi directory source globbing of text files',
    author='Michael Andersen',
    author_email='gosuckadeadcow+github@gmail.com',
    url='https://github.com/blackplague/multidirectorycorpusreader',
    packages=find_packages(exclude=('tests')),
)
