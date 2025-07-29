from setuptools import setup

setup(
    name="chivel",
    version="0.1.3",
    description="Chivel C++/Python extension",
    author="Mitchell Talyat",
    packages=["chivel"],
    package_dir={"chivel": "chivel"},
    package_data={"chivel": ["chivel.pyd", "chivel.pyi"]},
    include_package_data=True,
)