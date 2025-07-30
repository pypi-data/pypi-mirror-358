from setuptools import setup, find_packages

setup(
    name="ergs-selector",
    version="0.1.0",
    description="Effective Range-based Feature Selection (ERGS) for Classification",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your@email.com",
    url="https://github.com/yourusername/ergs-selector",
    packages=find_packages(),
    install_requires=["numpy", "pandas", "scikit-learn"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
