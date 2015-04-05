# coding=utf-8
import io
import os
import re
from setuptools import setup, find_packages


def get_path(*args):
    return os.path.join(os.path.dirname(__file__), *args)


def read_from(filepath):
    with io.open(filepath, 'rt', encoding='utf8') as f:
        return f.read()


def get_version(package):
    data = read_from(get_path(package, '__init__.py'))
    version = re.search(r"__version__\s*=\s*u?'([^']+)'", data).group(1)
    return str(version)


def get_description():
    return read_from(get_path('README.rst'))


def get_requirements(filename='requirements.txt'):
    data = read_from(get_path(filename))
    lines = map(lambda s: s.strip(), data.splitlines())
    requirements = [l for l in lines if l and not l.startswith('#')]
    return requirements


setup(
    name='Clay',
    version=get_version('clay'),
    author='Juan-Pablo Scaletti',
    author_email='juanpablo@lucumalabs.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    url='http://github.com/lucuma/Clay',
    license='MIT license (see LICENSE)',
    description='An amazing prototyping tool',
    long_description=get_description(),
    install_requires=get_requirements(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points={
        'console_scripts': ['clay = clay.manage:main'],
    },
)
