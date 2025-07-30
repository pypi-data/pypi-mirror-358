from setuptools import setup
import os
import re

def read_version():
    version_file = os.path.join('backtrader_contrib', 'version.py')
    with open(version_file, encoding='utf-8') as f:
        content = f.read()
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
    if not match:
        raise RuntimeError("Unable to find version string in version.py")
    return match.group(1)

def parse_requirements(filename='requirements.txt'):
    with open(filename, encoding='utf-8') as f:
        return [
            line.strip() for line in f
            if line.strip() and not line.startswith('#')
        ]

setup(
    version=read_version(),
    install_requires=parse_requirements(),
)
