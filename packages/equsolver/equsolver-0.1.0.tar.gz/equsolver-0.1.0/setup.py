from setuptools import setup, find_packages

setup(
    name='equsolver',
    version='0.1.0',
    description='Lightweight symbolic solver for equations',
    author='kkyian',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[],
)
