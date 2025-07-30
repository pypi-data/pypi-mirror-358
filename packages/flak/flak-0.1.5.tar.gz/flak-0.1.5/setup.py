from setuptools import setup, find_packages

setup(
    name="flak",
    version="0.1.5",
    description="",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="sultan",
    packages=find_packages(),
    include_package_data=True,
    package_data={"flak": ["data.txt"]},
    python_requires=">=3.7",
)
