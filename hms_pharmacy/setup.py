from setuptools import setup, find_packages

setup(
    name="hms_pharmacy",
    version="1.0.0",
    description="HMS Pharmacy - Inventory, formulary, dispensing, POS, batch/expiry management",
    author="Healthcare Team",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=["frappe", "hms_core"],
    python_requires=">=3.10",
)
