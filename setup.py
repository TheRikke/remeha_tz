from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='remeha_tz',
    version='0.12',
    packages=[],
    url='https://github.com/TheRikke/remeha_tz',
    license='',
    author='rikky',
    author_email='rikky@web.de',
    python_requires='>=3.6',
    data_files=[('config', ['config/translations.json'])],
    py_modules=['remeha', 'remeha_core', 'mqtt_logger', 'database_logger', 'datamap', 'plotlytest', 'remeha_info', 'remeha_convert'],
    scripts=['remeha.py', 'plotlytest.py', 'remeha_info.py', 'remeha_convert.py'],
    test_suite='tests',
    description='', install_requires=['dash', 'plotly', 'pyserial', 'paho-mqtt', 'mysql-connector-python'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
