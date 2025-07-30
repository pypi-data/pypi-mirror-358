from setuptools import setup, find_packages

setup(
    name='smscallbomber',
    packages=find_packages(),
    version='2.6',
    author='BabayVadimovich',
    author_email='hmatvej49@gmail.com',
    description='A library for SMS and call bomber / Библиотека для SMS бомбера со звонками',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/BabayVadimovich/SMSCallBomber',
    install_requires=[
        'requests',
        'asyncio',
        'argparse',
        'aiohttp'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords='bomber, sms, call, smsbomber',
)