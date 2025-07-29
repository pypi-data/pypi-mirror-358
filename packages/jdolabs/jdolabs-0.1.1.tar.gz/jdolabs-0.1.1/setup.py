from setuptools import setup, find_packages

setup(
    name="jdolabs",
    version="0.1.1",
    description="jdolabs cli framework for modular tool management and execution.",
    author="jdolabs",
    packages=find_packages(),  # This will include cli/ directory
    include_package_data=True,
    package_data={
        "": ["*.json", "*.txt"],  # Include JSON files in any package
        "cli": ["*.json", "*.txt", "commands/*.py"],  # Include cli files
    },
    entry_points={
        "console_scripts": [
            "jdolabs = main:main"
        ]
    },
    install_requires=[
        "typer>=0.9.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)