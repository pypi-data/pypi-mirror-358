from setuptools import setup, find_packages

setup(
    name="Youtube_package",
    version="0.1.0",
    author="abhishek chaudhary",
    description="A Jupyter-friendly YouTube embedding and metadata tool",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "requests",
        "IPython",
        "pytube"

    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
