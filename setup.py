import ast
import os
import os.path

from setuptools import find_packages, setup


def get_version():
    module_path = os.path.join(os.path.dirname(__file__),
                               'wikidata', '__init__.py')
    module_file = open(module_path)
    try:
        module_code = module_file.read()
    finally:
        module_file.close()
    tree = ast.parse(module_code, module_path)
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target, = node.targets
        if isinstance(target, ast.Name) and target.id == '__version__':
            value = node.value
            if isinstance(value, ast.Str):
                return value.s
            raise ValueError('__version__ is not defined as a string literal')
    raise ValueError('could not find __version__')


def readme():
    path = os.path.join(os.path.dirname(__file__), 'README.rst')
    try:
        with open(path) as f:
            return f.read()
    except IOError:
        pass


setup(
    name='Wikidata',
    version=get_version(),
    description='Wikidata client library',
    long_description=readme(),
    url='https://github.com/dahlia/wikidata',
    author='Hong Minhee',
    author_email='hong.minhee' '@' 'gmail.com',
    license='GPLv3 or later',
    packages=find_packages(exclude=['docs', 'tests']),
    python_requires='>=3.4.0',
    install_requires=['Babel >= 2.0'],
    keywords='wikidata ontology',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',  # noqa: E501
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Database',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
