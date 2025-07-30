from setuptools import setup, find_packages
from DA_Koyeb import  __version__

setup(
    name='koyeb',
    version=__version__,
    packages=find_packages(),
    install_requires=['flask'],
    python_requires='>=3.6',
    author='Alpha',
    author_email='imr@outlook.in',
    description='A Personal Python package to run apps seamlessly on Koyeb.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://t.me/North_Yankton',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)