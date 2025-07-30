# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

import sys
from setuptools import setup, find_packages
import versioneer

test_requirements = [
    'pytest>=3.0',
    'pytest-cov>=2.3.1',
    'pytest-timeout>=1.0',
    'flaky>=3.3.0',
    'nose>=1.3.7',
    'mne>=1.9.0',
    'scipy',
    'matplotlib',
    'tqdm>=4.62.3',
]

install_requires = ['mne>=1.9.0',
                    ]

# needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
# pytest_runner_requirement = ['pytest-runner>=2.9']

# setup_requires = pytest_runner_requirement if needs_pytest else []

# setup(
#     name='obci-readmanager',
#     version=versioneer.get_version(),
#     cmdclass=versioneer.get_cmdclass(),
#     zip_safe=False,
#     author='BrainTech',
#     author_email='admin@braintech.pl',
#     license='GNU General Public License v3 or later (GPLv3+)',
#     classifiers=[
#         'Development Status :: 3 - Alpha',
#         'Natural Language :: English',
#         'Topic :: Scientific/Engineering',
#         'Intended Audience :: Developers',
#         'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
#         'Programming Language :: Python :: 3',
#         'Programming Language :: Python :: 3.12',
#         'Operating System :: POSIX :: Linux',
#         'Environment :: Console',
#     ],
#     keywords='bci eeg openbci',
#     description='OpenBCI 2 readmanager support module',
#     packages=find_packages(exclude=['scripts', ]),
#     include_package_data=True,
#     exclude_package_data={'': ['.gitignore', '.gitlab-ci.yml']},
#     install_requires=install_requires,
#     tests_require=test_requirements,
#     setup_requires=setup_requires,
#     extras_require={
#         'test': pytest_runner_requirement + test_requirements,
#     },
# )


setup(
    name='readmanager',
    version=versioneer.get_version(),
    author='fuw_software',
    exclude_package_data={'': ['.gitignore', '.gitlab-ci.yml']},
    packages=find_packages(exclude=['scripts', ]),
    python_requires='>=3.12',
    tests_require=test_requirements,
    install_requires=install_requires
)
