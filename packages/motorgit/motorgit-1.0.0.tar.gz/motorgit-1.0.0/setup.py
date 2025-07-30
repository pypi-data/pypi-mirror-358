from setuptools import setup, find_packages
import Constants

setup(
    name = 'motorgit',
    version = Constants.version,
    packages = find_packages(),
    install_requires = [
        'click',
        'PyGithub',
        'keyring'
    ],
    entry_points = '''
    [console_scripts]
    motorgit=motorgit:motorgit
    ''',
    description = 'A simple tool to automate github uploads',
    long_description = open('Readme.md').read(),
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/AyushGupta0202/motorgit/',
    author = 'Ayush Gupta',
    author_email = 'ayushg430@gmail.com',
    license = 'MIT',
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires = '>=3.6',
)