from setuptools import setup, find_packages

setup(
    name="TST5",
    version="0.1.0",
    author="Konstantin",
    author_email="konstphx@gmail.com",
    description="Minimal library for TimeST5 time series instruction model inference",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "torch>=1.13.0",
        "transformers>=4.25.0",
        "numpy>=1.21.0",
        "safetensors>=0.3.0",
        "huggingface_hub>=0.15.0",
    ],
) 