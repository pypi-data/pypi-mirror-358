from setuptools import setup

setup(
    name='sendcyh',
    version='0.1.1',
    description='Send iOS Bark notifications easily to cyh.',
    author='cyh',
    author_email='isyuhaochen@gmail.com',
    packages=['sendcyh'],
    install_requires=['requests'],
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)