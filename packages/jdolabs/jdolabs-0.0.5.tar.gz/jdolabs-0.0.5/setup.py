from setuptools import setup, find_packages

setup(
    name="jdolabs",
    version="0.0.5",
    description="Core framework for managing JdoLabs modular tools and AI components.",
    author="JdoLabs",
    packages=find_packages(include=["cli", "logic", "config"]),
    include_package_data=True,
    package_data={
        "config": ["*.json", "*/*.json", "*.txt", "*/*.txt"],
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
