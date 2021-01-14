import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mshiznitzh", # Replace with your own username
    version="0.0.1",
    author="Mike Howard",
    author_email="mshiznitzh@gmail.com",
    description="Small program that use for my day to day task",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mshiznitzh/Pete_Maintenance_Helper/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)