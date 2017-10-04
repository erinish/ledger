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
        'flask',
        'flask_restful'
    ],
    entry_points='''
        [console_scripts]
        simplelog=simplelog.client:cli
    ''',
)
