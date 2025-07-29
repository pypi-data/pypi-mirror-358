from setuptools import setup, find_packages

setup(
    name="py-gradify",
    version="0.2.0",
    description="Apply gradient ANSI color to terminal text",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Rowan Barker",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
