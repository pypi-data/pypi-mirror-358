from setuptools import setup, find_packages

setup(
    name="windwoze",
    version="0.0.2",
    author="Annes",
    description="AppleTalk but windows",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
