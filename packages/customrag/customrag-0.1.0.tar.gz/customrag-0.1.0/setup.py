from setuptools import setup, find_packages

setup(
    name="customrag",
    version="0.1.0",
    author="Anuj Goel",
    description="A customizable RAG pipeline supporting multiple LLM providers and embedding backends.",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Automatically installs what's in requirements.txt
        line.strip() for line in open("requirements.txt") if line.strip() and not line.startswith("#")
    ],
    entry_points={
        "console_scripts": [
            "customrag-setup=customrag_setup:main",  # CLI command
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
