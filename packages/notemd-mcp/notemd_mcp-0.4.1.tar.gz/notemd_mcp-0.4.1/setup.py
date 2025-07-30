from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="notemd-mcp",
    version="0.4.1",
    description="A CLI tool for managing NoteMD projects.",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'notemd-mcp = notemd_mcp.main:start_server',
        ],
    },
)
