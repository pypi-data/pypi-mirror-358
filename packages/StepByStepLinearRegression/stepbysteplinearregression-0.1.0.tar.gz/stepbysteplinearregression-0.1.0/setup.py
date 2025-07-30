from setuptools import setup, find_packages

setup(
    name="StepByStepLinearRegression",
    version="0.1.0",
    author="mellamochiao",
    author_email="chou6855@gmail.com",
    description="A package for step-by-step regression analysis including simple, multiple, and logistic regression.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mellamochiao/StepByStepLinearRegression",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Mathematics"
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy",
        "pandas"
    ],
)
