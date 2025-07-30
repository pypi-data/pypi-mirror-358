from pathlib import Path

import setuptools

VERSION = "0.0.3"

NAME = "gump"

INSTALL_REQUIRES = [
    "aegypti>=0.3.2"
]

setuptools.setup(
    name=NAME,
    version=VERSION,
    description="Compute the Approximate Clique for undirected graph encoded in DIMACS format.",
    url="https://github.com/frankvegadelgado/gump",
    project_urls={
        "Source Code": "https://github.com/frankvegadelgado/gump",
        "Documentation Research": "https://dev.to/frank_vega_987689489099bf/gump-a-good-approximation-for-cliques-1304",
    },
    author="Frank Vega",
    author_email="vega.frank@gmail.com",
    license="MIT License",
    classifiers=[
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
    ],
    python_requires=">=3.12",
    # Requirements
    install_requires=INSTALL_REQUIRES,
    packages=["gump"],
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'fate = gump.app:main',
            'test_fate = gump.test:main',
            'batch_fate = gump.batch:main'
        ]
    }
)