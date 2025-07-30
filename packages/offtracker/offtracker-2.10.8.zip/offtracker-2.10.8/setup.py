#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io, os
# import sys
# from shutil import rmtree
from setuptools import setup

# import pkg_resources
from importlib_metadata import distribution
from setuptools.command.install import install
from setuptools.command.develop import develop

#
NAME = 'offtracker'
DESCRIPTION = 'Tracking-seq data analysis'
AUTHOR = 'Runda Xu'
EMAIL = 'xrd18@tsinghua.org.cn'
URL = 'https://github.com/Lan-lab/offtracker'
REQUIRES_PYTHON = '>=3.6.0'

here = os.path.abspath(os.path.dirname(__file__))

package_folder = NAME.lower().replace("-", "_").replace(" ", "_")
with open(os.path.join(here, package_folder, '_version.py'),'r',encoding='utf-8') as f:
    for line in f:
        if line.startswith("__version__"):
            VERSION = line.strip().split("=")[1].strip().replace('"', '')
            break

# requirements
REQUIRED = [
   'pandas', 'numpy', 'biopython', 'pybedtools', 'pyyaml', 
]
## pybedtools may be not supported in Windows

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION




class PostInstallCommand(install):
    def run(self):
        install.run(self)
        # 获取文件位置
        dist = distribution('offtracker')
        package_path = dist.locate_file('')
        utility_dir = os.path.join(package_path, 'offtracker/utility')
        os.chmod( os.path.join(utility_dir, 'bedGraphToBigWig'), 0o755)

class PostDevelopCommand(develop):
    def run(self):
        develop.run(self)
        # 获取文件位置
        dist = distribution('offtracker')
        package_path = dist.locate_file('')
        utility_dir = os.path.join(package_path, 'offtracker/utility')
        os.chmod( os.path.join(utility_dir, 'bedGraphToBigWig'), 0o755)

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    python_requires=REQUIRES_PYTHON,
    packages=['offtracker'],
    package_data={'offtracker': ['snakefile/*','utility/*']},
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    },
    scripts = ['scripts/offtracker_qc.py',
               'scripts/offtracker_config.py',
               'scripts/offtracker_candidates.py',
               'scripts/offtracker_analysis.py',
               'scripts/offtracker_plot.py'],
    install_requires=REQUIRED,
    include_package_data=True
)
