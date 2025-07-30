from setuptools import setup, find_packages

setup(
    name="libpx",
    version="5.0",
    description="End-to-end cryptography library including AES, RSA, OAEP, DH, and utilities.",
    author="Alfi Keita",
    author_email="",
    url="https://github.com/azrael1237/crypto",
    packages=find_packages(),
    install_requires=[
        "pyasn1",  # required for PEM/DER exports in px.py
    ],
    python_requires=">=3.6",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
    ],
    include_package_data=True,
)
