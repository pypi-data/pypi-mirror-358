from setuptools import setup

setup(
    name="jdolabs",
    version="0.0.2",
    py_modules=["main"],
    packages=["commands"],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'jdolabs = main:main',
        ],
    },
)
