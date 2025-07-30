from setuptools import setup, find_packages

setup(
    name='iranintl',
    version='0.1',
    packages=find_packages(exclude=['tests']), # TODO: maybe later add tests
    install_requires=[
        'requests',      
        'beautifulsoup4',
    ],
    author='Navid Poladi',
    author_email='navidpoladi99@example.com',
    description='A Python library to scrape data from Iran International news',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/navidpgg/iranintl',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)