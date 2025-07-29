from setuptools import setup, find_packages


VERSION = '0.0.1'
DESCRIPTION = 'Package to automate writing of (Open)TOPAS scripts, allowing for type inference and better access to parameters'


# Setting up
setup(
    name="topasio",
    version=VERSION,
    author="NeuralNine (Florian Dedov)",
    author_email="<mail@neuralnine.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'scripting', "automation", "writing"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)