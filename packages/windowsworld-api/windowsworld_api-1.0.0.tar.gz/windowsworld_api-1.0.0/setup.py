from setuptools import setup

setup(
    name='windowsworld-api',
    version='1.0.0',
    author='WindowsWorldCartoon',
    author_email='windowsworldcartoon@gmail.com',
    description='A Python client for the Windows World API',
    packages=['windowsworld_api'],
    install_requires=['requests'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)