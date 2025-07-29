from setuptools import setup, find_packages

setup(
    name='Code2cloudNB',
    version='0.1.0',
    author='Antick Mazumder',
    author_email='antick.majumder@gmail.com',
    description='A Python package providing helper functions to programmatically import Jupyter notebook content into Cloud platforms via REST APIs.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/antick-coder/Code2cloudNB.git',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)