from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="contextual-chunker",
    version="0.1.0",
    author="Kishan Tripathi",
    author_email="kishantripathi888@gmail.com",
    description="A comprehensive document chunking library with context generation for RAG applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KISHAN8888/contextual-chunker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "tqdm>=4.64.0",
        "python-dotenv>=0.19.0",
        "PyPDF2>=3.0.0",
        "PyMuPDF>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "contextual-chunker=contextual_chunker.cli:main",
        ],
    },
)