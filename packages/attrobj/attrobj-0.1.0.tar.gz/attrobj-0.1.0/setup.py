from setuptools import setup
from pathlib import Path

this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name='attrobj',
    version='0.1.0',
    packages=['attrobj'],
    url='https://github.com/fswair/custom_builtins',
    license='MIT',
    author='Mert Sirakaya',
    python_requires='>=3.10',
    long_description=long_description,
    long_description_content_type='text/markdown',
    description='A dictionary manipulator that enables attribute-style access to dictionary items.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13'
    ],
    install_requires=[],
)
