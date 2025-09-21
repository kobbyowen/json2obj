import pathlib

from setuptools import find_packages, setup

setup_dir = pathlib.Path(__file__).parent
readme_contents = (setup_dir / "README.md").read_text()

setup(
    name="json2obj",
    version="2.0.0",
    description="Convert your JSON data to a valid Python object to allow accessing keys with the member access operator(.) and more",
    long_description=readme_contents,
    long_description_content_type="text/markdown",
    url="https://github.com/kobbyowen/json2obj",
    author="Kobby Owen",
    author_email="dev@kobbyowen.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    include_package_data=True,
)
