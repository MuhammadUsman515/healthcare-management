from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

with open("README.md") as f:
    long_description = f.read()

setup(
    name="healthcare",
    version="1.0.0",
    description="Healthcare Management System built on Frappe/ERPNext",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Healthcare Team",
    author_email="healthcare@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.10",
)
