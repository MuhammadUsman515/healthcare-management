from setuptools import setup, find_packages

setup(
    name="hms_core",
    version="1.0.0",
    description="HMS Core - Shared masters, settings, identity, audit, notifications",
    author="Healthcare Team",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=["frappe"],
    python_requires=">=3.10",
)
