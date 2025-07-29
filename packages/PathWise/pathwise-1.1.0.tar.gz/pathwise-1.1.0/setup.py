from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="PathWise",
    version="1.1.0",
    author="Mahdi Jaffery",
    author_email="mahdijaffri5@gmail.com",
    description="A Python package implementing various search algorithms for maze solving",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MahdiJaffery/PathWise",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.6",
    install_requires=[
        "numpy>=1.19.0",
    ],
    keywords="maze search algorithms pathfinding BFS DFS A* UCS",
    project_urls={
        "Source": "https://github.com/MahdiJaffery/PathWise",
    },
)