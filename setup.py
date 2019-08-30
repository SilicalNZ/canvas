from setuptools import setup

setup(
    name = 'canvas',
    version = '',
    description = '',
    license = 'MIT',

    author = 'SilicalNZ',
    author_email = 'SilicalNZ@gmail.com',
    packages = ['canvas'],  #same as name
    install_requires = ['Pillow'], #external packages as dependencies
    common = ['common/common',
              'common/line_thingy',
              'common/sili_math'],
    tools = ['tools/alterations',
             'tools/shapes',
             'tools/sorters',
             'tools/transformers']
)
