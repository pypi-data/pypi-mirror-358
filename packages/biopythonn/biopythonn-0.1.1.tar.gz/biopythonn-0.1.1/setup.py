from setuptools import setup, find_packages

setup(
    name="biopythonn",
    version="0.1.1",
    author="Your Name",
    description="A Python library for biological data operations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
)
