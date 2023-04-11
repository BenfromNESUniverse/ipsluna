from setuptools import setup, find_packages

setup(
    name="get_patchlib",
    module = "patchlib",
    version="1.1",
    author="BrettefromNesUniverse",
    description="Patch file handler",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/BrettefromNesUniverse/patchlib",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    license="MIT",
)