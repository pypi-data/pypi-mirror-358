#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause

from pathlib    import Path

from setuptools import find_packages, setup

REPO_ROOT   = Path(__file__).parent
README_FILE = (REPO_ROOT / 'README.md')

def scm_version():
	def local_scheme(version):
		if version.tag and not version.distance:
			return version.format_with('')
		else:
			return version.format_choice('+{node}', '+{node}.dirty')
	return {
		'relative_to'   : __file__,
		'version_scheme': 'guess-next-dev',
		'local_scheme'  : local_scheme
	}

setup(
	name             = 'torii-boards',
	use_scm_version  = scm_version(),
	author           = ', '.join([
		'Aki Van Ness',
		'Rachel Mant',
	]),
	author_email     = ', '.join([
		'aki@lethalbit.net',
		'git@dragonmux.network',
	]),
	description      = 'Board and connector definitions for Torii-HDL',
	license          = ' BSD-2-Clause',
	python_requires  = '~=3.10',
	zip_safe         = True,
	url              = 'https://torii-boards.shmdn.link/',

	long_description = README_FILE.read_text(),
	long_description_content_type = 'text/markdown',

	setup_requires   = [
		'wheel',
		'setuptools',
		'setuptools_scm'
	],

	install_requires = [
		'torii>=0.8.0,<1.0',
	],

	extras_require   = {
		'dev': [
			'nox'
		],
	},

	packages         = find_packages(
		where   = '.',
		exclude = (
			'tests',
			'tests.*'
		)
	),
	package_data      = {
		'torii_boards': [
			'py.typed'
		],
	},

	classifiers       = [
		'Development Status :: 4 - Beta',

		'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',
		'Intended Audience :: Science/Research',

		'License :: OSI Approved :: BSD License',

		'Operating System :: MacOS :: MacOS X',
		'Operating System :: Microsoft :: Windows',
		'Operating System :: POSIX :: Linux',

		'Programming Language :: Python :: 3.10',
		'Programming Language :: Python :: 3.11',
		'Programming Language :: Python :: 3.12',
		'Programming Language :: Python :: 3.13',

		'Topic :: Scientific/Engineering',
		'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
		'Topic :: Software Development',
		'Topic :: Software Development :: Embedded Systems',
		'Topic :: Software Development :: Libraries',

		'Typing :: Typed',
	],

	project_urls     = {
		'Documentation': 'https://torii-boards.shmdn.link/',
		'Source Code'  : 'https://github.com/shrine-maiden-heavy-industries/torii-boards',
		'Bug Tracker'  : 'https://github.com/shrine-maiden-heavy-industries/torii-boards/issues',
	},
)
