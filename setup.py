from setuptools import setup

setup(
    name='cheggscraper',
    version='1.3',
    description='Convert Chegg url to complete html',
    packages=['cheggscraper'],
    install_requires=[
        'beautifulsoup4',
        'lxml',
        'requests',
        'jinja2',
    ],
    package_data={
        '': ['conf.json', 'template.html', 'chapter_type_frame.html'],
    },
    include_package_data=True
)
