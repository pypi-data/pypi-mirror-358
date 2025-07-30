from setuptools import setup, find_packages

setup(
    name="Texas_Extraction",
    version="0.1.2",
    description="Extract structured data from PDFs linked in Excel sheets.",
    author="Hamdi Emad",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "PyMuPDF",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "run-extractor=main:cli",
        ],
    },
)