from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lykos",
    version="0.0.1",
    author="oha",
    author_email="aaronoh2015@gmail.com",
    description="Git history secret detection, cleaning, and prevention tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/duriantaco/lykos",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "git-filter-repo>=2.38.0",
    ],
    entry_points={
        "console_scripts": [
            "lykos=lykos.cli:main",
            "lykos-scan=lykos.secret_scanner:main",
            "lykos-clean=lykos.git_secrets_cleaner:main",
            "lykos-guard=lykos.pre_commit_guard:main",
            "lykos-guardian=lykos.secret_guardian:main",
        ],
    },
)