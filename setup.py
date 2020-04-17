from setuptools import setup

setup(
    name='nmctl',
    version='0.1',
    py_modules=[],
    install_requires=[
        'click==7.0',
        'pandas==0.24.2',
    ],
    entry_points={'console_scripts': [
        'nmctl=nm.nmctl:cli'
    ]}
)
