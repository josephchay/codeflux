from setuptools import setup, find_packages
import subprocess
import os
from setuptools.command.develop import develop
from setuptools.command.install import install


def read_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()


class PostDevelopCommand(develop):
    def run(self):
        develop.run(self)
        self.execute(install_node_dependencies, (), msg="Installing Node.js dependencies...")
        self.execute(check_php_availability, (), msg="Checking PHP availability...")


class PostInstallCommand(install):
    def run(self):
        install.run(self)
        self.execute(install_node_dependencies, (), msg="Installing Node.js dependencies...")
        self.execute(check_php_availability, (), msg="Checking PHP availability...")


def install_node_dependencies():
    try:
        subprocess.check_call(['npm', '--version'], stdout=subprocess.PIPE)

        print("Installing JavaScript dependencies with npm...")
        subprocess.check_call(['npm', 'install'], cwd=os.path.dirname(os.path.abspath(__file__)))
        print("JavaScript dependencies installed successfully!")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Warning: npm not found. JS/TS, CSS, HTML, and PHP minification will be disabled.")
        print("To enable minification, install Node.js and run 'npm install' in the package directory.")


def check_php_availability():
    try:
        subprocess.check_call(['php', '-v'], stdout=subprocess.PIPE)
        print("PHP detected. PHP minification is available.")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Warning: PHP not found. PHP minification will be disabled.")
        print("To enable PHP minification, install PHP and ensure it's available in your PATH.")
        return False


setup(
    name="codeflux",
    version="0.9.0",
    description="A lightweight CLI tool to flatten, deflatten, bundle, and minify codebase files.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Joseph Chay",
    author_email="josephemmanuelchay@gmail.com",
    url="https://github.com/josephchay/codeflux",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    py_modules=["main", "constants", "utils", "handlers", "minify", "snipping", "search"],
    entry_points={
        "console_scripts": [
            "codeflux=main:main",
        ],
    },
    install_requires=read_requirements(),
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
    package_data={
        'src': ['scripts/minify/*.js', 'templates/*.csv'],
    },
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.12.7',
    ],
    python_requires=">=3.12.7",
    license="MIT",
    keywords="bundler, code-management, code-backup, code-archive, code-bundle",
    project_urls={
        "Documentation": "https://github.com/josephchay/codeflux/wiki",
        "Source": "https://github.com/josephchay/codeflux",
        "Tracker": "https://github.com/josephchay/codeflux/issues",
    },
)
