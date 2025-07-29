from setuptools import setup, find_packages

setup(
    name='pyionics',
    version='0.3.1',
    author='KamranHeydarov',
    packages = find_packages(),
    install_requires=[
        'requests',
        'pandas',
        'tqdm','os','csv','re','json']
)