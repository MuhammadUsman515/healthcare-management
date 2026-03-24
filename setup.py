from setuptools import setup, find_packages

setup(
    name="healthcare_management",
    version="1.0.0",
    description="Healthcare Management System - Frappe-based HMS with clinical, lab, pharmacy, revenue & portal modules",
    author="Healthcare Team",
    author_email="healthcare@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.10",
)
