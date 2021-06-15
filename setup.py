from setuptools import setup

setup(
    name='cheggscraper',
    version='1.1',
    description='Convert Chegg url to complete html',
    packages=['cheggscraper'],
    install_requires=[
        'beautifulsoup4',
        'lxml',
        'requests',
    ],
    package_data={
        '': ['conf.json', 'template.html'],
    },
    include_package_data=True
)
