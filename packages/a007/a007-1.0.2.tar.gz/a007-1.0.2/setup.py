from setuptools import setup, find_packages

setup(
    name="a007",
    version="1.0.2",
    author="Arshan Samani",
    author_email="your_email@example.com",
    description="A-007 Pro X Final - Ultra-secure hashing algorithm with customizable entropy-based encoding.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/a007",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography",
        "Development Status :: 5 - Production/Stable"
    ],
    python_requires='>=3.7',
    install_requires=[],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'a007=a007.__init__:hash_text',
        ]
    },
    keywords=["hash", "encryption", "security", "A-007", "cryptography", "custom hash"]
)
