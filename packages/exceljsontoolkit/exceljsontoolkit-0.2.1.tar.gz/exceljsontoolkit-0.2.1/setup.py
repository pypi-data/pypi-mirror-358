from setuptools import setup, find_packages

setup(
    name="exceljsontoolkit",
    version="0.2.1",
    author="Mahdi Jaffery",
    description="A toolkit to extract structured JSON from Excel, load it, and generate context maps.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/exceljsontoolkit",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "openai",
        "python-dotenv"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.7",
)
