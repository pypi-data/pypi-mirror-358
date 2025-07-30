from setuptools import setup, find_packages

# especifica explicitamente o encoding
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="DocuMiner",
    version="0.8.2",
    author="Sahib Ur rehman",
    author_email="rodrigonotion02@outlook.com",
    description="Advanced tool designed for text analysis and data mining in documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sabih-urrehman/documiner",
    packages=find_packages(),
    license='Apache',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
