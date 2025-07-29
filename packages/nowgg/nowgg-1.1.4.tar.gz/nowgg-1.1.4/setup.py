from setuptools import setup
from pathlib import Path
import os
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='nowgg',
    version='1.1.4',
    scripts=['nowgg.py'],
    author_email='cloudmaster@now.gg',
    install_requires=[
        'requests'
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'nowgg = nowgg:main',
        ],
    }
)