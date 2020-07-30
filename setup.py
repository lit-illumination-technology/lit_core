#!/usr/bin/python3
import setuptools

setuptools.setup(
    name="lit",
    version="0.1",
    author="Nick Pesce",
    author_email="nickpesce22@gmail.com",
    description="Lit Ilumination Technology",
    url=["https://github.com/nickpesce/lit"],
    packages=["lit", "lit.effects"],
    scripts=["bin/litd", "bin/litctl", "bin/litdev"],
    package_data={"lit": ["config/*"]},
    classifiers=["License :: MIT License", "Operating System :: Linux",],
)
