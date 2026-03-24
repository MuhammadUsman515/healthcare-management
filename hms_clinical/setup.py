from setuptools import setup, find_packages

setup(
    name="hms_clinical",
    version="1.0.0",
    description="HMS Clinical - OPD, IPD, EMR, encounters, nursing, procedures, discharge",
    author="Healthcare Team",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=["frappe", "hms_core"],
    python_requires=">=3.10",
)
