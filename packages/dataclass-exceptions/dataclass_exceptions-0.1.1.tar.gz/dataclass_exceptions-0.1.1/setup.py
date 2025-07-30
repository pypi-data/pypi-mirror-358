# noinspection PyProtectedMember
from setuptools import _install_setup_requires
_install_setup_requires(dict(setup_requires=[ 'extended-setup-tools' ]))

from extended_setup import ExtendedSetupManager

ExtendedSetupManager('dataclass_exceptions').setup \
(
    short_description = "A minimalist library for dataclass exceptions",
    category = 'libraries',
    min_python_version = '3.12',
    classifiers =
    [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
    ]
)
