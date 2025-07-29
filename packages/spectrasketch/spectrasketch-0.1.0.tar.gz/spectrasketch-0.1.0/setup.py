from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()
setup(
    name='spectrasketch',
    version='0.1.0',
    author='Swathi Baskar',
    description='A Python drawing library for custom shapes, rotation, and interactive editing using OpenCV.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='Apache-2.0',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.18.0',
        'opencv-python>=4.5.0'
    ],
    python_requires='>=3.6',
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
