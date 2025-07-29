from setuptools import setup, find_packages

setup(
    name='pyionics',
    version='0.3.2',
    author='KamranHeydarov',
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.0,<3.0.0',
        'pandas>=1.3.0,<3.0.0',
        'tqdm>=4.60.0,<5.0.0'
    ],
)
