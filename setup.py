from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('backpy/requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='backpy',
    version='0.0.8',
    author='Ridian',
    author_email='contact@ridian.io',
    description='Python vectorized backtester',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/ridian-io/backpy',
    packages=['backpy', 'backpy.sizers', 'backpy.stops', 'backpy.strategies' ],
    install_requires=required,
)
