import setuptools

setuptools.setup(
    name='lit',
    version='0.1',
    author='Nick Pesce',
    author_email='nickpesce22@gmail.com',
    description='Lit Ilumination Technology',
    url=['https://github.com/lit-illumination-technology/lit_core'],
    packages=['lit', 'lit.effects'],
    scripts=['bin/litctl', 'bin/litdev'],
    entry_points={
        'console_scripts': [
            'litd=lit.litd:start'
        ],
    },
    package_data={'lit': ['config/*']},
    classifiers=[
        'License :: MIT License',
        'Operating System :: Linux',
    ]
)
