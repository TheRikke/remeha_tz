from setuptools import setup

setup(
    name='remeha_tz',
    version='0.1',
    packages=[],
    url='',
    license='',
    author='rikky',
    author_email='',
    python_requires='>=3',
    data_files=[('config', ['config/translations.json'])],
    py_modules=['remeha', 'remeha_core', 'mqtt_logger', 'datamap', 'plotlytest', 'remeha_info', 'convert'],
    test_suite='tests',
    description='', install_requires=['dash', 'plotly', 'pyserial', 'paho-mqtt']
)
