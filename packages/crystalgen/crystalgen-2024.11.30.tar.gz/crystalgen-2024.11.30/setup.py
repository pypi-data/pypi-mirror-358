from setuptools import setup, find_packages

# Read in the README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="crystalgen",
    version="2024.11.30",
    author="Charles Campbell, Kamal Choudhary",
    author_email="kchoudh2@jhu.edu",
    description="CrystalGen: Generative atomistic materials design toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/atomgptlab/crystalgen",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.22.0",
        "scipy>=1.6.3",
        "jarvis-tools>=2021.07.19",
        "pydantic_settings",
        "pandas",  # Any other dependencies can be added here
        # "alignn",  # Uncomment if alignn becomes a required dependency
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    # entry_points={
    #     "console_scripts": [
    #         "run_atomgen=atomgen.run_atomgen:main", 
    #     ],
    # },
    include_package_data=True,
)
