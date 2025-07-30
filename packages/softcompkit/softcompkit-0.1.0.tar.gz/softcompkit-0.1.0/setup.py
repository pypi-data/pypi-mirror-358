from setuptools import setup, find_packages

setup(
    name="softcompkit",
    version="0.1.0",
    description="A toolkit for soft computing lab codes",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "scikit-learn"
    ],
    python_requires=">=3.6",
) 