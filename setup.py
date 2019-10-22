from setuptools import setup

setup(
    name='remeha_tz',
    version='0.1',
    packages=[],
    url='https://github.com/TheRikke/remeha_tz',
    license='',
    author='rikky',
    author_email='rikky@web.de',
    python_requires='>=3',
    data_files=[('config', ['config/translations.json'])],
    py_modules=['remeha', 'remeha_core', 'mqtt_logger', 'datamap', 'plotlytest', 'remeha_info', 'remeha_convert'],
    scripts=['remeha.py', 'plotlytest.py', 'remeha_info.py', 'remeha_convert.py'],
    test_suite='tests',
    description='', install_requires=['dash', 'plotly', 'pyserial', 'paho-mqtt']
)
