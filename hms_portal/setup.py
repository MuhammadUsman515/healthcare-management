from setuptools import setup, find_packages

setup(
    name="hms_portal",
    version="1.0.0",
    description="HMS Portal - Patient portal, doctor portal, lab portal, payments",
    author="Healthcare Team",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=["frappe", "hms_core"],
    python_requires=">=3.10",
)
