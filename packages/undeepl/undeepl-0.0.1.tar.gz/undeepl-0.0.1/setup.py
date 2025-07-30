from setuptools import setup, find_packages

setup(
    name="undeepl",
    version="0.0.1",
    description="(Reserved) Future DeepL unofficial Python API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Klypse",
    author_email="your@email.com",
    url="https://github.com/Klypse/UnDeepL",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
