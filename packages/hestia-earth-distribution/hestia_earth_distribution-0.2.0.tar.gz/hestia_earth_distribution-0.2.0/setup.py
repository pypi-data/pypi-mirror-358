import pathlib
from setuptools import find_packages, setup

from hestia_earth.distribution.version import VERSION

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / 'README.md').read_text()

REQUIRES = (HERE / 'requirements.txt').read_text().splitlines()

# This call to setup() does all the work
setup(
    name='hestia_earth_distribution',
    version=VERSION,
    description="Hestia's Distribution library",
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/hestia-earth/hestia-distribution',
    author='Hestia Team',
    author_email='guillaume@hestia.earth',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=('tests', 'scripts')),
    include_package_data=True,
    install_requires=REQUIRES,
    python_requires='>=3',
    extras_require={
        "stats": ["pymc", "scipy", "pandas"]
    }
)
