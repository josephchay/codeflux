from setuptools import setup, find_packages

def read_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()

setup(
    name="codebundle",
    version="0.7.0",
    description="A lightweight CLI tool to flatten, deflatten, and bundle codebase files.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Joseph Chay",
    author_email="josephemmanuelchay@gmail.com",
    url="https://github.com/josephchay/codebundle",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    py_modules=["main", "constants", "utils", "handlers"],
    entry_points={
        "console_scripts": [
            "codebundle=main:main",
        ],
    },
    install_requires=read_requirements(),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.12.7',
    ],
    python_requires=">=3.12.7",
    license="MIT",
    keywords="bundler, code-management, code-backup, code-archive, code-bundle",
    project_urls={
        "Documentation": "https://github.com/josephchay/codebundle/wiki",
        "Source": "https://github.com/josephchay/codebundle",
        "Tracker": "https://github.com/josephchay/codebundle/issues",
    },
)
