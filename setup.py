import pathlib
from setuptools import setup, find_packages

setup_dir = pathlib.Path(__file__).parent
readme_contents = (setup_dir / "README.md").read_text()

setup(
    name="json2obj",
    version="1.0.2",
    description="Convert your JSON data to a valid Python object to allow accessing keys with the member access operator(.)",
    long_description=readme_contents,
    long_description_content_type="text/markdown",
    url="https://github.com/trumpowen/json2obj",
    author="Owen Trump",
    author_email="trumpowen0@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    include_package_data=True
)
