from setuptools import setup, find_packages
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyionics',
    version='0.4.2',
    author='KamranHeydarov',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.0,<3.0.0',
        'pandas>=1.3.0,<3.0.0',
        'tqdm>=4.60.0,<5.0.0'
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
)
