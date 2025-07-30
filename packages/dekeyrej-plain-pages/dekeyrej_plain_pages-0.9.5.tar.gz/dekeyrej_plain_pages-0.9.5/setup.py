from setuptools import find_packages, setup

setup(
    name='plain_pages',
    packages=find_packages(include=['plain_pages']),
    version='0.9.5',
    description='Matrix Microservice and Client page superclasses',
    author='J.DeKeyrel',
    license='MIT',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)