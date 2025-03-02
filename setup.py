from setuptools import setup, find_packages

setup(
    name='codepeek',
    version='0.3.4',
    description='A lightweight CLI tool to flatten nested Python files into a single directory',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Joseph Chay',
    author_email='josephemmanuelchay@gmail.com',
    url='https://github.com/josephchay/codepeek',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'codepeek=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.7',
)
