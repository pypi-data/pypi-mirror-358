from setuptools import setup, find_packages

setup(
    name="polymerization_planner",
    version="0.1.3",
    description="A tool to generate polymerization reaction recipes from user-defined molar ratios and stock concentrations. Please see the PDF instruction in the GitHub link provided.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Cesar Ramirez",
    author_email="cr828@scarletmail.rutgers.edu",
    url="https://github.com/C3344/polymerization_planner/blob/main/polymerization_planner/docs/tutorial.pdf",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "openpyxl",
        "numpy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": ["polymerization-planner=polymerization_planner.main:main"]
    },
)
