from setuptools import setup, find_packages

setup(
    name='simplelog',
    version='0.1',
    packages=find_packages(),
    py_modules=['simplelog'],
    package_data={'simplelog.data':['*']},
    install_requires=[
        'Click',
        'Arrow',
        'requests',
        'click-shell',
    ],
    entry_points='''
        [console_scripts]
        aegiscli=aegiscli.main:cli
    ''',
)
