from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='ezx-pyapi',
    version='1.1.2',  # <-- Update this with each release
    license='MIT',
    author="EZX Inc.",
    author_email='support@ezxinc.com',
    packages=find_packages('.'),
    package_dir={'': '.'},
    url='https://www.ezxinc.com/',
    keywords='EZX iServer API trading',
    install_requires=[],
    description='EZX API client and message library for communicating with the iServer.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires=">=3.8, <4",
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    project_urls={
        'Sample API Application': 'https://github.com/EZXInc/ezx-sample-py',
        'Documentation' : 'https://github.com/EZXInc/ezx-sample-py/wiki',
        'Change Log' : 'https://github.com/EZXInc/ezx-sample-py/blob/master/CHANGELOG-API.md',
    }
)
