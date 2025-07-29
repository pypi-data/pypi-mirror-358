from setuptools import setup, find_packages

setup(
    name='cleantextify',
    version='0.1.6',
    packages=find_packages(),
    install_requires=[
        'emoji',
        
    ],
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    description='A lightweight Python package for cleaning text data.',
    author='Rajdeep18',
    author_email='rajdeeppandhere36coc@gmail.com',
    url='https://pypi.org/project/cleantextify/0.1.5/',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
