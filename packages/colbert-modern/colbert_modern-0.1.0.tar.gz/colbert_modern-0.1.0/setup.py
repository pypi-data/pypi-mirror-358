import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

package_data = {
    "": ["*.cpp", "*.cu"],
}

setuptools.setup(
    name="colbert-modern",
    version="0.1.0",
    author="Estin Chin",
    author_email="estin68@gmail.com",
    description="Updated ColBERT: Efficient and Effective Neural Retrieval",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stanford-futuredata/ColBERT",
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "bitarray",
        "datasets",
        "flask",
        "GitPython",
        "python-dotenv",
        "ninja",
        "scipy",
        "tqdm",
        "transformers",
        "ujson",
    ],
    extras_require={
        "faiss-gpu": ["faiss-gpu>=1.7.0"],
        "faiss-cpu": ["faiss-cpu>=1.7.0"],
        "torch": ["torch==1.13.1"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    include_package_data=True,
    package_data=package_data,
)
