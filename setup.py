from setuptools import setup, find_packages

setup(
    name='ledger',
    version='0.2',
    packages=find_packages(),
    py_modules=['ledger'],
    package_data={'ledger.data':['*']},
    install_requires=[
        'Click',
        'Arrow',
        'requests',
        'click-shell',
        'flask',
        'flask_restful'
    ],
    entry_points='''
        [console_scripts]
        ledger=ledger.client:cli
    ''',
)
