from setuptools import setup, find_packages

setup(
    name="basic_calculator_avik",
    version="1.0.0",
    author="avik-sarkar",
    author_email="aviksarkar44545@gmail.com",
    description="This is a basic calculator package that can do additions, subtractions, etc.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",  # ✅ This line is essential
    url="https://github.com/AvikSarkar0/Basic_Calculator.git",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "Calculator=Calculator.simple_calculator:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12',
)
