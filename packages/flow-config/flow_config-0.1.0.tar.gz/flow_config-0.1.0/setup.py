from setuptools import setup, find_packages

setup(
    name="flow-config",
    version="0.1.0",
    description="A Python library for event-driven configuration management",
    long_description=open("docs/source/README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Chinmay Sonawane",
    author_email="chinmaysonawane57@gmail.com",
    url="https://github.com/chinmay29hub/configflow",
    project_urls={
        "Homepage": "https://github.com/chinmay29hub/configflow",
        "Repository": "https://github.com/chinmay29hub/configflow.git",
        "Issues": "https://github.com/chinmay29hub/configflow/issues",
        "Documentation": "https://configflow.readthedocs.io/",
    },
    packages=find_packages(),
    install_requires=[
        "watchdog>=2.0",
        "PyYAML>=6.0",
        "orjson>=3.0",
        "pydantic>=2.0",
        "python-dotenv>=1.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=23.0",
            "isort>=5.0",
            "sphinx>=5.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.18",
            "types-setuptools",
            "types-PyYAML",
            "pylint>=3.0",
            "mypy>=1.0",
            "python-dotenv>=1.1",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
