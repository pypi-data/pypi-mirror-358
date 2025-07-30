from setuptools import setup, find_packages

setup(
    name="runwayapi",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.31.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.5.0"
    ],
) 