from setuptools import setup, find_packages

with open("smartpylogger/README.md", "r", encoding="utf-8") as f:
    long_description = f.read()
setup(
    name="smartpylogger",
    version="0.1.0",
    description="Lightweight structured logger for Py projects with AI analysis!",
    packages=find_packages(),
    # install_requires=[],  # or just remove this line entirely
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",  # or whichever license
    "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)

