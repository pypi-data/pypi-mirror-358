from setuptools import setup, Extension, find_packages
import os
import platform

# Define the extension module
ext_modules = [
    Extension(
        "tree_sitter_ballerina._binding",
        sources=[
            "bindings/python/tree_sitter_ballerina.c",
            "src/parser.c",
        ],
        include_dirs=["src"],
        extra_compile_args=['-std=c99'] if platform.system() != 'Windows' else [],
    ),
]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tree-sitter-ballerina",
    version="0.1.0",
    author="Heshan Padmasiri",
    author_email="",
    description="Ballerina grammar for tree-sitter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tree-sitter/tree-sitter-ballerina",
    packages=["tree_sitter_ballerina"],
    ext_modules=ext_modules,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Compilers",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.7",
    install_requires=[
        "tree-sitter>=0.20.0",
    ],
    zip_safe=False,
)