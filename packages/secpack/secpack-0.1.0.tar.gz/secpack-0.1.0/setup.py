from setuptools import setup, find_packages

setup(
    name="secpack",
    version="0.1.0",
    author="AleirJDawn",
    author_email="",
    description="secpack is a secure and flexible command-line tool for encrypting, decrypting, packaging, executing, and installing Python projects or arbitrary folders from local paths, URLs, or GitHub repositories.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),   
    python_requires='>=3.6',
    url="https://github.com/zwalloc/secpack", 
    install_requires=[
        'cryptography',
        'requests',
        'colorama',
    ],
    entry_points={     
        'console_scripts': [
            'secpack=secpack.main:main', 
        ],
    },
    classifiers=[      
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)

# cryptography, requests, colorama