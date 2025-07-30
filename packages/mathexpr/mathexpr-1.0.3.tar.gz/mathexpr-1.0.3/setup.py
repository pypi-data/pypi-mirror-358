from setuptools import setup, find_packages

setup(
    name='mathexpr',
    version='1.0.3',
    packages=find_packages(),
    install_requires=[

    ],
    author='griuc',
    author_email='griguchaev@yandex.ru',
    description='A library for parsing math strings',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/professionsalincpp/MathParse',
    license='MIT', 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)