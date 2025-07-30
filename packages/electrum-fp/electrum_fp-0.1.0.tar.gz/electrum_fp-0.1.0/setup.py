from setuptools import setup, find_packages

setup(
    name="electrum-fp",
    version="0.1.0",
    author="Markus Orsi",
    author_email="markus.orsi@unibe.ch",
    description="Metal-aware molecular fingerprinting tools",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "rdkit-pypi"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    keywords=["cheminformatics", "fingerprint", "electrum", "coordination"],
    python_requires=">=3.7",
    include_package_data=True,
)