from setuptools import setup, find_packages

setup(
    name="recode_geohash",
    version="0.1.0",
    author="Recode Team",
    description="Codificação e decodificação de geohash com geração de vizinhos.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/recode_geohash",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
