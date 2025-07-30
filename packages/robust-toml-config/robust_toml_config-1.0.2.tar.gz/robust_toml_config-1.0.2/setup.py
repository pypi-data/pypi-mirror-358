from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="robust-toml-config",
    version="1.0.2",
    author="wzs",
    author_email="83241568@qq.com",
    description="Robust TOML configuration manager with format preservation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/wzs83241568/robust-toml-config",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=["tomlkit>=0.11.0"],
    extras_require={
        "dev": ["pytest>=6.0", "twine>=3.0"],
    },
    project_urls={
        "Bug Reports": "https://gitee.com/wzs83241568/robust-toml-config/issues",
        "Source": "https://gitee.com/wzs83241568/robust-toml-config",
    },
)