from setuptools import setup

setup(
    name='arknights-resources-calculator',
    version='1.0.0',
    description='A useful module for Arknights spent resources calculation',
    author='MaxEhrhart',
    author_email='',
    packages=['arknights'],  # same as name
    install_requires=['numpy==1.21.4', 'pandas==1.3.4', 'XlsxWriter==3.0.2', 'pandas-xlsx-tables==0.0.5']  # dependency
)
