import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyPMS",
    version="0.0.1",
    author="XuanShine",
    author_email="xuan.ng@hotmail.com",
    description="PMS (Property Management System) for Hotel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/XuanShine/PyPMS",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
