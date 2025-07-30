from setuptools import find_namespace_packages, setup

VERSION = '2.0.1'

setup(
    name="NEMO-stockroom",
    version=VERSION,
    description="Stockroom plugin for NEMO",
    packages=find_namespace_packages(),
    author="David J. Jones",
    author_email="davijon@seas.upenn.edu",
    url="https://gitlab.com/nemo-community/upenn/nemo-stockroom-cart",
    include_package_data=True,
    install_requires=[
        "django",
    ],
    extras_require={
        "NEMO-CE": ["NEMO-CE>=1.7.0"],
        "NEMO": ["NEMO>=4.7.0"],
        "dev-tools": ["pre-commit", "djlint", "black"],
    },
    keywords=["NEMO"],
)
