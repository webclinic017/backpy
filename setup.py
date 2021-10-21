import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('backpy/requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name='backpy',
    version='0.0.1',
    author='Ridian',
    author_email='contact@ridian.io',
    description='Python vectorized backtester',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/ridian-io/backpy',
    packages=['backpy'],
    install_requires=required,
)