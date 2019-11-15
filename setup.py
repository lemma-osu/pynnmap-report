from setuptools import setup, find_packages

import pynnmap_report

setup(
    name='pynnmap_report',
    version=pynnmap_report.__version__,
    url='http://github.com/lemma-osu/pynnmap-report/',
    author='LEMMA group @ Oregon State University',
    author_email='matt.gregory@oregonstate.edu',
    packages=find_packages(),
    description='Report generation for pynnmap accuracy assessment',
    install_requires=[
        'click',
        'matplotlib',
        'numpy',
        'pandas',
        'pynnmap',
        'reportlab',
        'six',
        'scipy'
    ],
    entry_points='''
        [pynnmap.cli_commands]
        old-report=pynnmap_report.cli.old_report:old_report
        report=pynnmap_report.cli.report:report
    ''',
)
