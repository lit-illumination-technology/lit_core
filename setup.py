import setuptools

setuptools.setup(
    name="lit-core",
    version="0.0.1",
    author="Nick Pesce",
    author_email="nickpesce22@gmail.com",
    description="Lit Ilumination Technology",
    url="https://github.com/lit-illumination-technology/lit_core",
    packages=["lit", "lit.effects"],
    scripts=["bin/litctl", "bin/litdev"],
    entry_points={"console_scripts": ["litd=lit.litd:start"],},
    package_data={"lit": ["config/*"]},
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Topic :: Home Automation",
    ],
    install_requires=["rpi_ws281x"],
    python_requires=">=3.5",
)
