from setuptools import setup, find_packages

setup(
    name='fusionMLlib',
    version='0.1.0',
    description='A one-stop ML meta-package for all essential libraries',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line and not line.startswith("#")
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.7',
)