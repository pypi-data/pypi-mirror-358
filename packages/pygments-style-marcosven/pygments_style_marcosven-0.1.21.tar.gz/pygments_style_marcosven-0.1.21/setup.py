from setuptools import setup, find_packages

setup(
    name="pygments-style-marcosven",
    version="0.1.021",
    packages=find_packages(),
    entry_points={
        'pygments.styles': [
            'marcoSven = marco_sven:MarcoSvenStyle',
        ],
    },
    author="marcoSven",
    author_email="me@marcoSven.com",
    description="Custom Pygments style for Aider",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/marcoSven/pygments-style-marcosven",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=["pygments>=2.0"],
    python_requires=">=3.7",
)
