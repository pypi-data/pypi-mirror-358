from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyterminal-emulator",
    version="1.1.0",
    author="Aarav Shah",
    author_email="aaravprogrammers@gmail.com",
    description="A Linux Terminal Emulator development Package for various os",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ap1311/pyterminal-emulator",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Topic :: System :: Shells",
    ],
    install_requires=[
        'requests',
        'pycurl',
    ],
    entry_points={
        'console_scripts': [
            'pyterminalx=pyterminalx.commands:main',
        ],
    },
)